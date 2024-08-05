from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('office_user/', views.office_user_page, name='office_user_page'),
    path('register_entry/', views.register_entry, name='register_entry'),
    path('register_exit/', views.register_exit, name='register_exit'),
    path('office_manager/', views.office_manager_page, name='office_manager_page'),
]
