from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Clock, OfficeUser, OfficeManager, Leave, RegularRequest
from .forms import OfficeUserForm, RegularRequestForm
from django.contrib.auth.models import User 

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
    return render(request, 'office_user_page.html')

@login_required
def register_entry(request):
    if request.method == "POST":
        office_user = get_object_or_404(OfficeUser, user=request.user)
        Clock.objects.create(office_user=office_user, entry_to_office=timezone.now())
        return JsonResponse({"status": "success", "message": "Entry time registered."})
    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

@login_required
def register_exit(request):
    if request.method == "POST":
        office_user = get_object_or_404(OfficeUser, user=request.user)
        clock_entry = Clock.objects.filter(office_user=office_user).latest('entry_to_office')
        clock_entry.exit_from_office = timezone.now()
        clock_entry.save()
        return JsonResponse({"status": "success", "message": "Exit time registered."})
    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

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
        form = OfficeUserForm(request.POST)
        if form.is_valid():
            office_user = form.save(commit=False)
            office_user.office_admin = office_manager
            office_user.save()
            # automatically create the user with phone as username and code_meli as password
            office_user.user = User.objects.create_user(
                username=office_user.phone,
                password=office_user.code_meli
            )
            office_user.save()
            return redirect('office_manager_page')
    else:
        form = OfficeUserForm()

    return render(request, 'add_office_user.html', {'form': form})

@login_required
def leave_page(request):
    if request.method == "POST":
        office_user = get_object_or_404(OfficeUser, user=request.user)
        
        # Handling Hourly Leave Request
        hourly_start_time = request.POST.get('hourly_start_time')
        hourly_end_time = request.POST.get('hourly_end_time')
        
        if hourly_start_time and hourly_end_time:
            Leave.objects.create(
                office_user=office_user,
                leave_type='hourly',
                start_time=hourly_start_time,
                end_time=hourly_end_time,
                leave_date=timezone.now().date()  # Assume leave is taken on the current date
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
                reason=leave_reason
            )

        return redirect('office_user_page')
    
    return render(request, 'leave_page.html')

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