from email.mime import base
from django.urls import path, include 
 
from rest_framework.authtoken import views as token_views
from rest_framework.routers import DefaultRouter

from . import views     

app_name = 'accounts_api'

# router = DefaultRouter()
# router.register('users', views.CustomUserModelViewSets, basename='users')
 

urlpatterns = [  
    path('users/', views.CustomUserAPIView.as_view()),
    path('users/<int:pk>/', views.CustomUserAPIView.as_view()),
    path('users/my-details/', views.MyAccountView.as_view()),
    path('users/forget-password/', views.ForgetPasswordView.as_view()),
    path('users/forget-password/<token>/', views.ResetPasswordView.as_view(), name='reset-password' ),

    # path('get-my-token/', token_views.obtain_auth_token),
    path('login/', token_views.obtain_auth_token),
    path('users/add-certificate/', views.AddCertificateAPIView.as_view()),

] 
# + router.urls