from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
    path('download-qr-pdf/', views.download_qr_pdf, name='download_qr_pdf'),
    path('register-user/', views.register_user, name='register_user'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('view-orders/', views.view_orders, name='view_orders'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('logout/', views.admin_logout, name='logout'),
    path('register-external-user/', views.external_user_registration, name='external_register'),
    path('send-notification/<str:user_id>/', views.check_id_enabled, name='check_id_enabled'),
    path('activate-id/<str:user_id>/', views.activate_id, name='activate_id'),
    path('send-notification-final/<str:user_id>/', views.send_notification, name='send_notification'),

]
