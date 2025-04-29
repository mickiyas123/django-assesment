"""
Views for the users app.
"""
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

# Configure logger
logger = logging.getLogger(__name__)

User = get_user_model()

# Create your views here.

class RegisterView(generics.CreateAPIView):
    """
    Register a new user with email, password, and role.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's information.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    """
    Logout a user by blacklisting their refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    """
    Request a password reset email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            reset_link = f"http://localhost:8000/reset-password/{uid}/{token}/"
            
            subject = "Password Reset Request"
            html_message = f"""
            <html>
            <head></head>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello {user.first_name or user.email},</p>
                <p>You requested a password reset for your account. Please click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>If you didn't request this, you can safely ignore this email.</p>
                <p>The link will expire in 24 hours.</p>
                <p>Thank you,<br>Your Application Team</p>
            </body>
            </html>
            """
            plain_message = strip_tags(html_message)
            
            # Send email
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
                logger.info(f"Password reset email sent to {email} with link: {reset_link}")
                return Response({
                    "message": "Password reset email has been sent. Please check your inbox."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")
                return Response({
                    "error": f"Failed to send email: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in password reset: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetConfirmView(APIView):
    """
    API view to confirm password reset and set a new password.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            uid = request.data.get('uid')
            token = request.data.get('token')
            new_password = request.data.get('new_password1')
            
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                
                try:
                    subject = "Password Reset Successful"
                    html_message = render_to_string('users/password_reset_success_email.html', {
                        'user': user,
                    })
                    plain_message = strip_tags(html_message)
                    
                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=html_message,
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to send confirmation email: {str(e)}")
                
                return Response({"success": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid token. The link may have expired."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError) as e:
            logger.error(f"Error decoding user ID: {str(e)}")
            return Response({"error": "Invalid reset link format."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error in password reset confirm: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GoogleLoginView(SocialLoginView):
    """
    View for handling Google OAuth login.
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://localhost:8000/accounts/google/login/callback/"
