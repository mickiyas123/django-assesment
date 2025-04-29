from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, 
    UserDetailView, 
    LogoutView, 
    PasswordResetView, 
    PasswordResetConfirmView,
    GoogleLoginView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User profile
    path('me/', UserDetailView.as_view(), name='user_detail'),
    
    # Social authentication
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    
    # Password reset
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
] 