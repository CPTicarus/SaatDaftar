from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Clock, OfficeUser, OfficeManager, Leave, Project
from .forms import OfficeUserForm, RegularRequestForm, ProjectForm
from django.contrib.auth.models import User 
from django.db import IntegrityError 
from django.contrib import messages

#To redirect logins 
@login_required
def dashboard(request):
    user = request.user  # Get the logged-in user

    if OfficeUser.objects.filter(user=user).exists():
        return redirect('office_user_page')
    elif OfficeManager.objects.filter(user=user).exists():
        return redirect('office_manager_page')
    else:
        return redirect('login')

@login_required
def office_user_page(request):
    # Get the OfficeUser object related to the current user
    office_user = get_object_or_404(OfficeUser, user=request.user)
    return render(request, 'office_user_page.html', {'office_user': office_user})

@login_required
def register_entry(request):
    if request.method == "POST":
        office_user = get_object_or_404(OfficeUser, user=request.user)
        # Check if there's an active entry (entry without an exit)
        active_clock = Clock.objects.filter(office_user=office_user, exit_from_office__isnull=True).exists()
        if active_clock:
            return JsonResponse({"status": "error", "message": "You have already registered an entry. Please register an exit before registering a new entry."}, status=400)
        Clock.objects.create(office_user=office_user, entry_to_office=timezone.now())
        return JsonResponse({"status": "success", "message": "Entry time registered."})
    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

@login_required
def register_exit(request):
    if request.method == "POST":
        office_user = get_object_or_404(OfficeUser, user=request.user)
        # Find the last clock entry that has no exit
        active_clock = Clock.objects.filter(office_user=office_user, exit_from_office__isnull=True).order_by('-entry_to_office').first()
        if not active_clock:
            return JsonResponse({"status": "error", "message": "No active entry found. Please register an entry before registering an exit."}, status=400)
        active_clock.exit_from_office = timezone.now()
        active_clock.save()
        return JsonResponse({"status": "success", "message": "Exit time registered."})
    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

@login_required
def get_clock_status(request):
    office_user = get_object_or_404(OfficeUser, user=request.user)
    
    entry_count = Clock.objects.filter(office_user=office_user).count()
    exit_count = Clock.objects.filter(office_user=office_user, exit_from_office__isnull=False).count()
    
    can_register_entry = entry_count == exit_count
    can_register_exit = entry_count > exit_count
    
    return JsonResponse({
        'can_register_entry': can_register_entry,
        'can_register_exit': can_register_exit
    })

@login_required
def office_manager_page(request):
    office_manager = get_object_or_404(OfficeManager, user=request.user)
    employees = OfficeUser.objects.filter(office_admin=office_manager)

    employee_statuses = []
    for employee in employees:
        # Check if the employee is in the office
        last_clock_entry = Clock.objects.filter(office_user=employee).order_by('-entry_to_office').first()
        is_in_office = last_clock_entry and not last_clock_entry.exit_from_office

        # Check if the employee has a pending or ongoing leave request
        now = timezone.now()
        has_leave_request = Leave.objects.filter(
            office_user=employee,
            leave_type='daily',
            start_date__lte=now,
            end_date__gte=now
        ).exists() or Leave.objects.filter(
            office_user=employee,
            leave_type='hourly',
            start_time__lte=now,
            end_time__gte=now
        ).exists()

        employee_statuses.append((employee, is_in_office, has_leave_request))

    context = {
        'office_manager': office_manager,
        'employees': employee_statuses,
    }
    
    return render(request, 'office_manager_page.html', context)

@login_required
def add_office_user(request):
    office_manager = get_object_or_404(OfficeManager, user=request.user)

    if request.method == "POST":
        form = OfficeUserForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Check if a user with the same phone number already exists
                if User.objects.filter(username=form.cleaned_data['phone']).exists():
                    messages.error(request, 'An error occurred. The phone number is already associated with an existing user.')
                else:
                    # First, create a new User instance with the phone number as the username and code meli as the password
                    user = User.objects.create_user(
                        username=form.cleaned_data['phone'],
                        password=form.cleaned_data['code_meli']
                    )
                    
                    # Now create the OfficeUser instance and link it to the User instance
                    office_user = form.save(commit=False)  # Create OfficeUser without saving to the database yet
                    office_user.user = user  # Link the User instance
                    office_user.office_admin = office_manager  # Set the logged-in office manager as the office admin
                    office_user.save()  # Save the OfficeUser instance to the database

                    messages.success(request, f'Office user {office_user.first_name} {office_user.last_name} was created successfully.')
                    return redirect('office_manager_page')
            except IntegrityError:
                messages.error(request, 'An unexpected error occurred. Please try again.')
        else:
            messages.error(request, 'There was an error in the form. Please correct the errors below.')
    else:
        form = OfficeUserForm()

    return render(request, 'add_office_user.html', {'form': form})

@login_required
def leave_page(request):
    office_user = get_object_or_404(OfficeUser, user=request.user)
    
    if request.method == "POST":
        # Handling Hourly Leave Request
        hourly_start_time = request.POST.get('hourly_start_time')
        hourly_end_time = request.POST.get('hourly_end_time')
        
        if hourly_start_time and hourly_end_time:
            Leave.objects.create(
                office_user=office_user,
                leave_type='hourly',
                start_time=hourly_start_time,
                end_time=hourly_end_time,
                approved=None  # Set to None to mark as pending by default
            )

        # Handling Daily Leave Request
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        leave_reason = request.POST.get('leave_reason')

        if start_date and end_date:
            Leave.objects.create(
                office_user=office_user,
                leave_type='daily',
                start_date=start_date,
                end_date=end_date,
                reason=leave_reason,
                approved=None  # Set to None to mark as pending by default
            )

        return redirect('office_user_page')
    
    # Fetch the user's leave requests
    leave_requests = Leave.objects.filter(office_user=office_user).order_by('-start_date', '-start_time')

    return render(request, 'leave_page.html', {
        'leave_requests': leave_requests
    })

@login_required
def approve_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    
    # Only allow office managers to approve leave
    if hasattr(request.user, 'officemanager'):  # Ensure the user has an associated OfficeManager
        leave.approved = True
        leave.save()
        return redirect('employee_detail', employee_id=leave.office_user.id)
    else:
        return HttpResponseForbidden("You do not have permission to perform this action.")

@login_required
def deny_leave(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    
    # Only allow office managers to deny leave
    if hasattr(request.user, 'officemanager'):  # Ensure the user has an associated OfficeManager
        leave.approved = False
        leave.save()
        return redirect('employee_detail', employee_id=leave.office_user.id)
    else:
        return HttpResponseForbidden("You do not have permission to perform this action.")
    
@login_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(OfficeUser, id=employee_id)

    # Get the employee's last clock entry
    last_clock_entry = Clock.objects.filter(office_user=employee).order_by('-entry_to_office').first()

    # Get the employee's leave requests
    leave_requests = Leave.objects.filter(office_user=employee).order_by('-start_date')

    context = {
        'employee': employee,
        'last_clock_entry': last_clock_entry,
        'leave_requests': leave_requests,
    }
    
    return render(request, 'employee_detail.html', context)

@login_required
def submit_request(request):
    if request.method == 'POST':
        form = RegularRequestForm(request.POST)
        if form.is_valid():
            regular_request = form.save(commit=False)
            regular_request.user = request.user.officeuser  # Associate with the logged-in user
            regular_request.save()
            return redirect('office_user_page')
    else:
        form = RegularRequestForm()

    return render(request, 'submit_request.html', {'form': form})

@login_required
def project_page(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)  # Save the form data without committing to the DB
            project.save()  # Now commit to the DB
            form.save_m2m()  # Save many-to-many relationships, required for assigned_users
            
            messages.success(request, 'Project created successfully!')  # Add success message
            return redirect('project_page')
    else:
        form = ProjectForm()

    projects = Project.objects.all()

    context = {
        'form': form,
        'projects': projects,
    }
    return render(request, 'project_page.html', context)

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, f'Project "{project.name}" has been successfully deleted.')
        return redirect('project_page')

    context = {
        'project': project,
    }

@login_required
def end_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.end_date is None:  # Ensure that the project does not already have an end date
        project.end_date = timezone.now().date()
        project.save()
        messages.success(request, f'Project "{project.name}" has been successfully ended.')

    return redirect('project_page')

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" has been successfully updated.')
            return redirect('project_page')
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'edit_project.html', context)