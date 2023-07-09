from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (ActivityLogListAPIView, ServiceProviderListCreateAPIView, StaffListCreateAPIView, 
                    EmailOTPAPIView, ResetPasswordAPIView, LogoutAPIView, StaffDetailAPIView, 
                    ServiceProviderDetailAPIView, ActivityLogDetailAPIView, VerifyOTPAPIView,
                    StaffPermissionSetAPIView, StaffAccessResetAPIView, StaffAccessRevokeAPIView,
                    StaffPermissionDetailAPIView, StaffPermissionListAPIView, ServiceProviderToggleStatusAPIView,
                    LoginAPIView)

app_name = 'uacs'


urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('activity-log/', ActivityLogListAPIView.as_view(), name='activity_log_list'),
    path('activity-log/<int:pk>', ActivityLogDetailAPIView.as_view(), name='activity_log_detail'),
    path('service_providers/', ServiceProviderListCreateAPIView.as_view(), name="sp_list_create" ),
    path('service_providers/<int:pk>/', ServiceProviderDetailAPIView.as_view(), name="sp_detail" ),
    path('service_providers/<int:pk>/status_toggle/', ServiceProviderToggleStatusAPIView.as_view(), name="sp_toggle_status" ),
    path('staffs/', StaffListCreateAPIView.as_view(), name="staff_list_create"),
    path('staffs/<int:pk>/', StaffDetailAPIView.as_view(), name="staff_detail"),
    path('staff/<int:pk>/revoke/', StaffAccessRevokeAPIView.as_view(), name='revoke'),
    path('staff/<int:pk>/reset/', StaffAccessResetAPIView.as_view(), name='reset'),
    path('email_otp/', EmailOTPAPIView.as_view(), name="email_otp"),
    path('verify_otp/', VerifyOTPAPIView.as_view(), name="verify_otp"),
    path('reset_password', ResetPasswordAPIView.as_view(), name="reset_password"),
    path('permission_set/', StaffPermissionSetAPIView.as_view(), name="set_permission"),
    path('staff_permission/<int:pk>/', StaffPermissionDetailAPIView.as_view(), name="staff_permission_detail"),
    path('staff_permissions/', StaffPermissionListAPIView.as_view(), name="staff_permission_list"),
]