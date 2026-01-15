from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='registration'),
    path('auth/register/<str:referral_code_used>/', RegisterView.as_view(), name='registration_with_referral'),
    path('auth/user/', UserDetailView.as_view(), name='user_detail'),
    path('auth/active/user/', UserRegistrationVerifyCodeView.as_view(), name='verify_code'),
    path('auth/resend/code/', ResendCodeView.as_view(), name='resend_code'),
    path('auth/login/', TokenObtainPairView.as_view(), name='access_token'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/verify_code/', VerifyCodeView.as_view(), name='verify_code'),
    path('auth/set_new_password/', SetNewPasswordView.as_view(), name='set_new_password'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # update profile
    path('auth/profile/update/', UpdateProfileView.as_view(), name='profile-update'),
    path('user/profile/<int:pk>/', UserTriggerView.as_view(), name='user-trigger'),
    path('auth/user/list/', UserListView.as_view(), name='user-list'),
    path('auth/user/notification/toggle/', NotificationToggleview.as_view(), name='user-notification-toggle'),
    
    
    # promocode
    path('auth/promo-code/', PromoCodeView.as_view(), name='promo_code'),
    path('auth/promo-code/<int:pk>/', PromoCodeDetailView.as_view(), name='promo_code_detail'),
]
