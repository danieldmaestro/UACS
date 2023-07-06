from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (ActivityLogListAPIView, ServiceProviderListCreateAPIView, StaffListCreateAPIView, 
                    EmailOTPAPIView, ResetPasswordAPIView)

app_name = 'uacs'


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('activity-log/', ActivityLogListAPIView.as_view(), name='activity_log_list'),
    path('service_providers/', ServiceProviderListCreateAPIView.as_view(), name="sp_list_create" ),
    path('staffs/', StaffListCreateAPIView.as_view(), name="staff_list_create"),
    path('email_otp/', EmailOTPAPIView.as_view(), name="email_otp"),
    path('reset_password', ResetPasswordAPIView.as_view(), name="reset_password"),
]