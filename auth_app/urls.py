from django.contrib import admin
from django.urls import path, include
from auth_app.views import UserCreate, UserDetailView, google_login_callback, validate_google_token, confirm_email, CustomObtainTokenPairView, current_user
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('user/register/', UserCreate.as_view(), name='user_create'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('current-user/', current_user, name='current_user'),
    path('auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('callback/', google_login_callback, name='google_callback'),
    path('auth/user/', UserDetailView.as_view(), name='user_detail'),
    path('google/validate_token/', validate_google_token, name='validate_google_token'),
    path('register/', UserCreate.as_view(), name='register'),
    path('confirm_email/<uidb64>/<token>/', confirm_email, name='confirm_email'),
    path('token/', CustomObtainTokenPairView.as_view(), name='token_obtain_pair'),
]
