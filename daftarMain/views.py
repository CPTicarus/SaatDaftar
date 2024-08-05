from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Clock, OfficeUser, OfficeManager

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

# @login_required
# def start_temporary_exit(request):
#     if request.method == "POST":
#         office_user = get_object_or_404(OfficeUser, user=request.user)
#         clock_entry = Clock.objects.filter(office_user=office_user).latest('entry_to_office')
#         clock_entry.wait_time_start = timezone.now()
#         clock_entry.save()
#         return JsonResponse({"status": "success", "message": "Temporary exit time started."})
#     return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

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

    context = {
        'office_manager': office_manager,
        'employees': employees,
    }
    
    return render(request, 'office_manager_page.html', context)
