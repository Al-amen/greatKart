from django.urls import path
from .import views
app_name = 'accounts'

urlpatterns = [
     path('register/', views.RegisterView.as_view(), name='register'),
     path('login/', views.LoginView.as_view(), name='login'),
     path('logout/', views.CustomLogoutView.as_view(), name='logout'),
     path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate'),
     path('',views.DashboardView.as_view(),name="dashboard"),

     path('forgot-password/',views.ForgotPassword.as_view(),name='forgot-password'),
     path('password-reset-validate/<uidb64>/<token>/',views.ResetPasswordValidate.as_view(),name='password-reset-validate'),
     path('reset-password',views.ResetPassword.as_view(),name='reset-password'),

     path('my-orders/',views.MyOrdersView.as_view(),name='my-orders'),
     path('edit-profile/',views.EditProfileView.as_view(),name='edit-profile'),
     path('change-password/',views.ChangePasswordView.as_view(),name='change-password'),
     path('order-detail/<str:order_number>/',views.OrderDetailView.as_view(),name='order-detail'),
     


    

]
