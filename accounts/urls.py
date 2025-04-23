from django.urls import path
from .import views
app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
   
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
     path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate'),
     path('',views.DashboardView.as_view(),name="dashboard")
    

]
