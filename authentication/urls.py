from django.urls import path
from rest_framework_simplejwt.tokens import RefreshToken
from .views import (
RegisterView,
VerifyEmail,
LoginView,PasswordTokenCheckAPI,
RequestPasswordResetEmail, setNewPasswordAPIView,
LogoutAPIView,
ChangePasswordView,
UpdateProfileView
)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutAPIView.as_view(),name='logout'),
    path('email-verify/',VerifyEmail.as_view(),name='email-verify'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
    path('request-reset-email/',RequestPasswordResetEmail.as_view(),name='request-reset-email'),
    path('password-reset/<uidb64>/<token>',PasswordTokenCheckAPI.as_view(),name='password-reset-confirm'),
    path('password-reset-complete/',setNewPasswordAPIView.as_view(),name='password-reset-complete'),
    path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='change_password'),
    path('update_profile/<int:pk>/', UpdateProfileView.as_view(), name='update_profile'),
    
]
