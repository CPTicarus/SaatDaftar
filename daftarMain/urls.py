from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    #Office manager urls
    path('office_manager/', views.office_manager_page, name='office_manager_page'),
    path('office_manager/add-user/', views.add_office_user, name='add_office_user'),
    path('employee/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('projects/', views.project_page, name='project_page'),
    #office users urls
    path('register_entry/', views.register_entry, name='register_entry'),
    path('register_exit/', views.register_exit, name='register_exit'),
    path('office_user/', views.office_user_page, name='office_user_page'),
    path('leave/', views.leave_page, name='leave_page'),
    path('submit_request/', views.submit_request, name='submit_request'),
    path('get_clock_status/', views.get_clock_status, name='get_clock_status'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
