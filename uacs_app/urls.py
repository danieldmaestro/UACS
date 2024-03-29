from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (ActivityLogListAPIView, ServiceProviderCreateAPIView, StaffListAPIView, StaffCreateAPIView, 
                    EmailOTPAPIView, ResetPasswordAPIView, LogoutAPIView, StaffDetailAPIView, 
                    ServiceProviderDetailAPIView, ActivityLogDetailAPIView, VerifyOTPAPIView,
                    StaffPermissionSetAPIView, StaffAccessResetAPIView, StaffAccessRevokeAPIView,
                    StaffPermissionDetailAPIView, StaffPermissionListAPIView, ServiceProviderToggleStatusAPIView,
                    LoginAPIView, ServiceProviderListAPIView, SecurityLogListAPIView, DashboardCountAPIView,
                    StaffPermissionUpdateAPIView, ActiveStaffListAPIView,ActiveServiceProviderListAPIView,
                    TrackedSitesAPIView)

app_name = 'uacs'


urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('activity_log/', ActivityLogListAPIView.as_view(), name='activity_log_list'),
    path('activity_log/<int:pk>/', ActivityLogDetailAPIView.as_view(), name='activity_log_detail'),
    path('security_log/', SecurityLogListAPIView.as_view(), name='security_log_list'),
    path('service_providers/all/', ServiceProviderListAPIView.as_view(), name="sp_list" ),
    path('service_providers/active/', ActiveServiceProviderListAPIView.as_view(), name="active_sp_list" ),
    path('service_providers/create/', ServiceProviderCreateAPIView.as_view(), name="sp_create" ),
    path('service_providers/<int:pk>/', ServiceProviderDetailAPIView.as_view(), name="sp_detail" ),
    path('service_providers/<int:pk>/status_toggle/', ServiceProviderToggleStatusAPIView.as_view(), name="sp_toggle_status" ),
    path('staffs/all/', StaffListAPIView.as_view(), name="staff_list"),
    path('staffs/create/', StaffCreateAPIView.as_view(), name="staff_list"),
    path('staffs/active/', ActiveStaffListAPIView.as_view(), name="active_staff"),
    path('staffs/<int:pk>/', StaffDetailAPIView.as_view(), name="staff_detail"),
    path('staffs/<int:pk>/revoke/', StaffAccessRevokeAPIView.as_view(), name='revoke'),
    path('staffs/<int:pk>/reset/', StaffAccessResetAPIView.as_view(), name='reset'),
    path('email_otp/', EmailOTPAPIView.as_view(), name="email_otp"),
    path('verify_otp/', VerifyOTPAPIView.as_view(), name="verify_otp"),
    path('reset_password', ResetPasswordAPIView.as_view(), name="reset_password"),
    path('permission_set/', StaffPermissionSetAPIView.as_view(), name="set_permission"),
    path('staff_permission/<int:pk>/', StaffPermissionDetailAPIView.as_view(), name="staff_permission_detail"),
    path('staff_permissions/', StaffPermissionListAPIView.as_view(), name="staff_permission_list"),
    path('staff_permissions/update/', StaffPermissionUpdateAPIView.as_view(), name="staff_permission_update"),
    path('count/', DashboardCountAPIView.as_view(), name="dashboard_count"),
    path('tracked_sites/', TrackedSitesAPIView.as_view(), name="tracked_sites"),
]