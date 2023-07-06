from django.shortcuts import render
from rest_framework import generics

from .models import ActivityLog
from .serializers import (StaffSerializer,ServiceProviderSerializer, StaffPermissionSerializer,
                            ActivityLogSerializer)

# Create your views here.


class StaffListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StaffSerializer


class ServiceProviderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ServiceProviderSerializer


class ActivityLogListAPIView(generics.ListAPIView):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer


