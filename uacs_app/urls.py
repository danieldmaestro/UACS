from django.urls import path
from .views import ActivityLogListAPIView, ServiceProviderListCreateAPIView, StaffListCreateAPIView

app_name = 'uacs'


urlpatterns = [
    path('activity-log/', ActivityLogListAPIView.as_view(), name='activity_log_list'),
    path('service_providers/', ServiceProviderListCreateAPIView.as_view(), name="sp_list_create" ),
    path('staffs/', StaffListCreateAPIView.as_view(), name="staff_list_create"),
]