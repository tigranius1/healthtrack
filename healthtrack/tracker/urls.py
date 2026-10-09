from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.measurement_add, name='measurement_add'),
    path('delete/<int:pk>/', views.measurement_delete, name='measurement_delete'),
    path('export/', views.export_csv, name='export_csv'),

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tracker/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]