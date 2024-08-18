from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request_handler/', views.request_handler, name='request_handler'),
    path('staff_management/', views.staff_management, name='staff_management'),
    
    # Office manager URLs
    path('office_manager/', views.office_manager_page, name='office_manager_page'),
    path('office_manager/add-user/', views.add_office_user, name='add_office_user'),
    
    # Employee-related URLs
    path('employee/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employee/<int:employee_id>/registered-hours/', views.calculate_hours, name='registered_hours'),
    path('employee/<int:employee_id>/delete-hour/<int:entry_id>/', views.delete_registered_hour, name='delete_registered_hour'),
    path('employee/<int:employee_id>/add-reward-punishment/', views.add_reward_punishment, name='add_reward_punishment'),
    path('employee/<int:employee_id>/edit/', views.edit_employee, name='edit_employee'),

    # Leave management URLs
    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/deny/<int:leave_id>/', views.deny_leave, name='deny_leave'),

    # Project-related URLs
    path('projects/', views.project_page, name='project_page'),
    path('projects/end/<int:project_id>/', views.end_project, name='end_project'),
    path('project/<int:project_id>/', views.detail_project, name='detail_project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),

    # Office users urls
    path('register_entry/', views.register_entry, name='register_entry'),
    path('register_exit/', views.register_exit, name='register_exit'),
    path('project-popup/', views.project_popup, name='project_popup'),
    path('get_clock_status/', views.get_clock_status, name='get_clock_status'),

    path('office_user/', views.office_user_page, name='office_user_page'),
    path('leave/', views.leave_page, name='leave_page'),
    path('submit_request/', views.submit_request, name='submit_request'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
