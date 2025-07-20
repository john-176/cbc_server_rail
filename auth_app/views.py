from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.conf import settings


from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status


User = get_user_model()

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status




class CustomObtainTokenPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Get the user credentials
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user and user.is_active:
            # If the user is active, proceed to generate tokens
            return super().post(request, *args, **kwargs)
        else:
            # If the user is not active, return an error response
            return Response(
                {'detail': 'Account not confirmed or deactivated.'},
                status=status.HTTP_400_BAD_REQUEST
            )

# Function to send verification email
def send_verification_email(user, request):
    # Generate email verification token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())

    # Generate the verification link
    verification_url = f"http://localhost:8000/api/verify-email/{uid}/{token}/"

    # Email subject and message
    subject = "Verify Your Email Address"
    message = render_to_string("email_verification.html", {
        "user": user,
        "verification_url": verification_url
    })

    # Send the email
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

# Updated register user view
class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Create the user but keep it inactive until email is verified
        user = serializer.save()
        user.is_active = False  # Deactivate the user until email is verified
        user.save()

        # Send the verification email
        send_verification_email(user, self.request)

        # Optionally, you can redirect to a front-end confirmation page or send a message
        return redirect("http://localhost:5173/check-email")

    
@login_required
def google_login_callback(request):
    user = request.user
    
    social_accounts = SocialAccount.objects.filter(user=user)
    print("Social Accounts for user:", social_accounts)
    
    social_account = social_accounts.first()
    
    if not social_account:
        print("No social account found for user", user)
        return redirect('http://localhost:5173/login/callback/?error=No social account found')
    token = SocialToken.objects.filter(user=social_account, account__provider='google').first()
    
    if token:
        print('Google token found:', token.token)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return redirect(f'http://localhost:5173/login/callback/?access_token={access_token}')
    else:
        print("No google token found for user", user)
        return redirect('http://localhost:5173/login/callback/?error=NoGoogleToken')

@csrf_exempt
def validate_google_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            google_access_token = data.get('access_token')
            print(google_access_token)

            if not google_access_token:
                return JsonResponse({'detail': 'Access token is missing or not provided.'}, status=400)
            return JsonResponse({'valid': True})
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON data.'}, status=400)
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)
      
      
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from django.http import JsonResponse



#@login_required
# views.py
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

@authentication_classes([JWTAuthentication])

def current_user(request):
    return JsonResponse({
        'is_authenticated': True,
        'username': request.user.username,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
    })

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user



def confirm_email(request, uidb64, token):
    try:
        # Decode the user ID from the URL
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    # Validate the token
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate the user
        user.save()
        return redirect('http://localhost:5173/login?message=Account confirmed, please log in.')
    else:
        return render(request, 'email/confirmation_invalid.html')  # Handle invalid token
