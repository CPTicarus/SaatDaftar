from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from django.contrib import messages

from django.db import IntegrityError
from django.db.models import Sum, F

from datetime import datetime, timedelta
from collections import defaultdict

from .models import Clock, OfficeUser, OfficeManager, Leave, Project, ProjectTimeLog
from .forms import OfficeUserForm, RegularRequestForm, ProjectForm, ProjectSelectionForm

#To redirect logins 
@login_required
def dashboard(request):
    user = request.user

    if OfficeUser.objects.filter(user=user).exists():
        return redirect('office_user_page')
    elif OfficeManager.objects.filter(user=user).exists():
        return redirect('office_manager_page')
    else:
        return redirect('login')

@login_required
def office_user_page(request):
    office_user = get_object_or_404(OfficeUser, user=request.user)
    assigned_projects = office_user.projects.all()
    
    context = {
        'office_user': office_user,
        'projects': assigned_projects,  # Pass only the assigned projects
    }
    
    return render(request, 'office_user_page.html', context)

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
    office_user = get_object_or_404(OfficeUser, user=request.user)

    if request.method == "POST":
        # Get the most recent clock entry
        clock_entry = Clock.objects.filter(office_user=office_user).order_by('-entry_to_office').first()

        if clock_entry and clock_entry.exit_from_office is None:
            # Register the exit time
            clock_entry.exit_from_office = timezone.now()
            clock_entry.save()

            time_spent = clock_entry.exit_from_office - clock_entry.entry_to_office
            assigned_projects = office_user.projects.all()

            # Handle the selected projects
            project_ids = request.POST.getlist('projects')
            selected_projects = assigned_projects.filter(id__in=project_ids)
            num_projects = selected_projects.count()

            if num_projects > 0:
                # Divide the total time spent across the selected projects
                time_per_project = time_spent / num_projects

                for project in selected_projects:
                    # Log the time in the ProjectTimeLog
                    ProjectTimeLog.objects.create(
                        office_user=office_user,
                        project=project,
                        hours_spent=time_per_project.total_seconds() / 3600.0  # Convert seconds to hours
                    )

                    # Add the project to the clock entry
                    clock_entry.projects.add(project)

            return JsonResponse({'message': 'Exit time registered successfully and projects updated.'})
        else:
            return JsonResponse({'message': 'No active entry found or exit already registered.'}, status=400)

    return JsonResponse({'message': 'Invalid request.'}, status=400)

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
                if User.objects.filter(username=form.cleaned_data['phone']).exists():
                    messages.error(request, 'The phone number is already associated with an existing user.')
                else:
                    office_user = form.save(commit=False)
                    user = User.objects.create_user(
                        username=form.cleaned_data['phone'],
                        password=form.cleaned_data['code_meli']
                    )
                    office_user.user = user
                    office_user.office_admin = office_manager
                    office_user.save()

                    messages.success(request, f'Office user {office_user.first_name} {office_user.last_name} was created successfully.')
                    return redirect('office_manager_page')
            except IntegrityError as e:
                error_message = str(e)
                if 'UNIQUE constraint failed' in error_message:
                    print("Unique constraint violation: Phone number already exists.")
                else:
                    messages.success(request, 'Office user was created successfully.')
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

    # Get the employee's pending leave requests
    leave_requests = Leave.objects.filter(office_user=employee, approved=None).order_by('-start_date')

    context = {
        'employee': employee,
        'last_clock_entry': last_clock_entry,
        'leave_requests': leave_requests,
    }
    
    return render(request, 'employee_detail.html', context)

@login_required
def edit_employee(request, employee_id):
    employee = OfficeUser.objects.get(id=employee_id)
    user = employee.user

    if request.method == "POST":
        form = OfficeUserForm(request.POST, request.FILES, instance=employee)

        if form.is_valid():
            form.save()

            new_username = request.POST.get('new_username')
            new_password = request.POST.get('new_password')

            # Update the username if provided
            if new_username and new_username != user.username:
                if User.objects.filter(username=new_username).exists():
                    messages.error(request, 'The username is already taken.')
                else:
                    user.username = new_username
                    user.save()

            # Update the password if provided
            if new_password:
                user.set_password(new_password)
                user.save()

            messages.success(request, f'{employee.first_name} {employee.last_name} has been updated successfully.')
            return redirect('employee_detail', employee_id=employee.id)

    else:
        form = OfficeUserForm(instance=employee)

    return render(request, 'edit_employee.html', {
        'form': form,
        'employee': employee,
    })

@login_required
def project_popup(request):
    if request.method == 'POST':
        form = ProjectSelectionForm(request.POST)
        if form.is_valid():
            selected_projects = form.cleaned_data['projects']
            # You can now process the selected projects, for example, saving them to the database
            for project in selected_projects:
                pass
            return redirect('success_page')  # Redirect to a success page or close the popup
    else:
        form = ProjectSelectionForm()
    
    return render(request, 'project_popup.html', {'form': form})

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
def detail_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Get optional date range filter from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Convert the date strings to date objects if provided
    if start_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

    # Calculate total hours worked on the project
    total_hours = 0
    user_contributions = {}

    for entry in project.clock_entries.all():
        if start_date and entry.entry_to_office.date() < start_date:
            continue
        if end_date and entry.exit_from_office.date() > end_date:
            continue

        hours_worked = entry.hours_worked()  # Calculate hours worked
        total_hours += hours_worked

        if entry.office_user in user_contributions:
            user_contributions[entry.office_user] += hours_worked
        else:
            user_contributions[entry.office_user] = hours_worked

    # Convert total hours into hours and minutes
    total_hours_int = int(total_hours)
    total_minutes = int((total_hours - total_hours_int) * 60)

    # Convert user contributions to hours and minutes
    user_contributions_converted = {}
    for office_user, hours in user_contributions.items():
        hours_int = int(hours)
        minutes = int((hours - hours_int) * 60)
        user_contributions_converted[office_user] = f"{hours_int} hours {minutes} minutes"

    context = {
        'project': project,
        'total_hours': f"{total_hours_int} hours {total_minutes} minutes",
        'start_date': start_date,
        'end_date': end_date,
        'user_contributions': user_contributions_converted,
    }
    return render(request, 'detail_project.html', context)


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

@login_required
def calculate_hours(request, employee_id):
    employee = get_object_or_404(OfficeUser, id=employee_id)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    clock_entries = []
    total_hours = 0

    if start_date and end_date:
        # Filter clock entries by the given date range and ensure exit_from_office is not None
        clock_entries = Clock.objects.filter(
            office_user=employee,
            entry_to_office__gte=start_date,
            exit_from_office__lte=end_date,
            exit_from_office__isnull=False
        )

        # Calculate the total time worked
        total_seconds_worked = clock_entries.aggregate(
            total_worked=Sum(F('exit_from_office') - F('entry_to_office'))
        )['total_worked']

        if total_seconds_worked:
            total_hours = total_seconds_worked.total_seconds() / 3600  # Convert to hours

        # Calculate hours worked for each entry and attach it to the entry
        for entry in clock_entries:
            entry.hours_worked = (entry.exit_from_office - entry.entry_to_office).total_seconds() / 3600

    return render(request, 'registered_hours.html', {
        'employee': employee,
        'clock_entries': clock_entries,
        'total_hours': total_hours,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def delete_registered_hour(request, employee_id, entry_id):
    # Fetch the entry using entry_id and employee_id for validation
    entry = get_object_or_404(Clock, id=entry_id, office_user_id=employee_id)
    entry.delete()
    messages.success(request, "The entry has been successfully deleted.")

    return redirect('registered_hours', employee_id=employee_id)

@login_required
def add_reward_punishment(request, employee_id):
    employee = get_object_or_404(OfficeUser, id=employee_id)

    if request.method == "POST":
        date = request.POST.get('date')
        hours = float(request.POST.get('hours'))
        action_type = request.POST.get('type')

        # Convert the date to a datetime object
        date_time = timezone.make_aware(datetime.strptime(date, "%Y-%m-%d"))

        # Calculate the exit time based on the hours and action type
        if action_type == "punishment":
            hours = -hours  # Subtract hours for punishment

        exit_time = date_time + timedelta(hours=hours)

        # Create a Clock entry with the calculated entry and exit times
        Clock.objects.create(
            office_user=employee,
            entry_to_office=date_time,
            exit_from_office=exit_time,
            is_reward_punishment=True,
        )

        messages.success(request, f'Successfully added a {action_type} of {hours} hours for {employee.first_name} {employee.last_name}.')
        return redirect('registered_hours', employee_id=employee.id)

    return render(request, 'registered_hours.html', {'employee': employee})

def calculate_project_hours(project, start_date=None, end_date=None):
    
    if start_date is None:
        start_date = timezone.datetime.min.date()
    if end_date is None:
        end_date = timezone.now().date()

    # Fetch the time logs within the date range
    time_logs = ProjectTimeLog.objects.filter(
        project=project,
        log_date__range=(start_date, end_date)
    )
    
    total_hours = sum(log.hours_spent for log in time_logs)
    
    return total_hours

