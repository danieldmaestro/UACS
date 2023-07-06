import random
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from accounts.models import User
from .models import ActivityLog, Staff
from .serializers import (StaffSerializer,ServiceProviderSerializer, StaffPermissionSerializer,
                            ActivityLogSerializer, EmailOTPSerializer, ResetPasswordSerializer,
                            VerifyOTPSerializer)
from .tasks import send_otp_mail

# Create your views here.

def generate_otp():
    # Generate a random 6-digit OTP code
    return str(random.randint(100000, 999999))


class StaffListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StaffSerializer


class ServiceProviderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ServiceProviderSerializer


class ActivityLogListAPIView(generics.ListAPIView):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer


class EmailOTPAPIView(generics.CreateAPIView):
    serializer_class = EmailOTPSerializer

    def perform_create(self, serializer):
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).get()
        if user:
            otp = generate_otp()
            user.verification_code = otp
            # Send the OTP code to the provided email
            subject='OTP Code'
            message = f'Your OTP code is: {otp}'
            send_otp_mail.delay(subject=subject, recipient=[email], message=message,)
            return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
        return Response({'message': 'No staff with this email is registered.'}, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyOTPAPIView(generics.UpdateAPIView):
    serializer_class = VerifyOTPSerializer
    queryset = User.objects.all()

    def get_object(self):
        email = self.request.data.get('email')
        try:
            user = self.queryset.filter(email=email).get()
        except self.model.DoesNotExist:
            user = None
        return user
    
    def perform_update(self, serializer):
        user = self.get_object()
        otp_code = serializer.validated_data['otp_code']

        if user.verification_code == otp_code:
            user.verification_code = ""
            user.save()
            return Response({'message': 'Verification code is valid.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Verification code is invalid.'}, status=status.HTTP_400_BAD_REQUEST)
        

class ResetPasswordAPIView(generics.UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    queryset = User.objects.all()

    def get_object(self):
        email = self.request.data.get('email')
        verification_code = self.request.data.get('verification_code')
        try:
            user = self.queryset.filter(email=email, verification_code=verification_code).get()
        except self.model.DoesNotExist:
            user = None
        return user

    def perform_update(self, serializer):
        user = self.get_object()
        if user is None:
            return Response({'message': 'Verification code'}, status=status.HTTP_400_BAD_REQUEST)
        password = serializer.validated_data['password']
        user.set_password(password)
        return Response({'message': 'Password updated successfully'}, status=status.HTTP_202_ACCEPTED)


    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     if instance is None:
    #         return Response({'message': 'Verification code'}, status=status.HTTP_400_BAD_REQUEST)
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         instance._prefetched_objects_cache = {}
    #     return Response({'message': 'Password updated successfully'}, status=status.HTTP_202_ACCEPTED)

    # def perform_update(self, serializer):
    #     serializer.save()





