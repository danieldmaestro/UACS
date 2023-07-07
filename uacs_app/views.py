import random
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from .mixins import ActivityLogMixin
from .models import ActivityLog, Staff, Tribe, Squad, Designation, ServiceProvider, StaffPermission
from .serializers import (StaffSerializer,ServiceProviderSerializer, StaffPermissionSerializer,
                            ActivityLogSerializer, EmailOTPSerializer, ResetPasswordSerializer,
                            VerifyOTPSerializer)
from .tasks import send_otp_mail
from .utils import create_permissions

# Create your views here.

def generate_otp():
    # Generate a random 6-digit OTP code
    return str(random.randint(100000, 999999))

class LogoutAPIView(ActivityLogMixin, generics.GenericAPIView):

    def get_serializer_class(self):
        return None
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class StaffListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    queryset = Staff.objects.all()

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        tribe_name = serializer.validated_data.pop('tribe_name')
        squad_name = serializer.validated_data.pop('squad_name')
        designation_name = serializer.validated_data.pop('designation_name')
        tribe = get_object_or_404(Tribe, name__iexact=tribe_name)
        squad = get_object_or_404(Squad, name__iexact=squad_name)
        designation = get_object_or_404(Designation, name__iexact=designation_name)
        staff = serializer.save(
            tribe=tribe, squad=squad, designation=designation
        )
        create_permissions(staff)
        return Response({'message': 'Staff created succesfully'}, status=status.HTTP_201_CREATED)
    

class StaffDetailAPIView(generics.RetrieveAPIView):
    serializer_class = StaffSerializer
    queryset = Staff.objects.all()
    permission_classes = [IsAuthenticated]


class StaffAccessResetAPIView(generics.UpdateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = True
        instance.save()
        return Response({'message': 'Staff access reset successfully.'}, status=status.HTTP_200_OK)
    

class StaffAccessRevokeAPIView(generics.UpdateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({'message': 'Staff access revoked successfully.'}, status=status.HTTP_200_OK)


class ServiceProviderListCreateAPIView(ActivityLogMixin, generics.ListCreateAPIView):
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]
    queryset = ServiceProvider.objects.all()

    def perform_create(self, serializer):
        service_provider = serializer.save()
        service_provider.save()
        for staff in Staff.objects.all():
            StaffPermission.objects.create(staff=staff, service_provider=service_provider)

        return Response({'message': 'Service Provider created succesfully'}, status=status.HTTP_201_CREATED)


class ServiceProviderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ServiceProviderSerializer
    queryset = ServiceProvider.objects.all()
    permission_classes = [IsAuthenticated]



class ActivityLogListAPIView(generics.ListAPIView):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]


class ActivityLogDetailAPIView(generics.RetrieveAPIView):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]


class EmailOTPAPIView(generics.GenericAPIView):
    serializer_class = EmailOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.filter(email=email).get()
            otp = generate_otp()
            print(otp)
            user.verification_code = otp
            user.save()
            # Send the OTP code to the provided email
            subject = 'OTP Code'
            message = f'Your OTP code is: {otp}'
            send_otp_mail.delay(subject=subject, recipient=[email], message=message)
            return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'No staff with this email is registered.'}, status=status.HTTP_400_BAD_REQUEST)
 

class VerifyOTPAPIView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = VerifyOTPSerializer

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            user = self.queryset.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'This email is not associated with any user.'}, status=status.HTTP_400_BAD_REQUEST)
             
        if user and user.verification_code == otp_code:
            user.verification_code = ""
            user.save()
            return Response({'message': 'Verification code is valid.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Verification code is invalid.'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(generics.UpdateAPIView):
    serializer_class = ResetPasswordSerializer
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
        if user is None:
            return Response({'message': 'No user associated with this email'}, status=status.HTTP_400_BAD_REQUEST)
        password = serializer.validated_data['password']
        user.set_password(password)
        return Response({'message': 'Password updated successfully'}, status=status.HTTP_202_ACCEPTED)
    

class StaffPermissionSetAPIView(generics.GenericAPIView):

    serializer_class = StaffPermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff_list = serializer.validated_data.pop("staff_list")
        sp_list = serializer.validated_data.pop("sp_list")
        sp_object_list = [get_object_or_404(ServiceProvider, id=sp_id) for sp_id in sp_list]

        for staff_id in staff_list:
            staff = get_object_or_404(Staff, id=staff_id)
            staff.sp_permissions.filter(service_provider__in=sp_object_list).values_list("is_permitted", flat=True).update(is_permitted=True)
        
        return Response({'message': 'Permission granted for selected staff and service providers'}, status=status.HTTP_201_CREATED)


class StaffPermissionDetailAPIView(generics.RetrieveAPIView):
    queryset = StaffPermission.objects.all()
    serializer_class = StaffPermissionSerializer
    lookup_field = 'pk'




class StaffPermissionListAPIView(generics.ListAPIView):
    serializer_class = StaffPermissionSerializer
    queryset = StaffPermission.objects.all()

    








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

       

# class VerifyOTPAPIView(generics.UpdateAPIView):
#     serializer_class = VerifyOTPSerializer
#     queryset = User.objects.all()

#     def get_object(self):
#         email = self.request.data.get('email')
#         try:
#             user = self.queryset.filter(email=email).get()
#         except self.model.DoesNotExist:
#             user = None
#         return user
    
#     def perform_update(self, serializer):
#         user = self.get_object()
#         otp_code = serializer.validated_data['otp_code']

#         if user.verification_code == otp_code:
#             user.verification_code = ""
#             user.save()
#             return Response({'message': 'Verification code is valid.'}, status=status.HTTP_200_OK)
#         return Response({'message': 'Verification code is invalid.'}, status=status.HTTP_400_BAD_REQUEST)
        

# class EmailOTPAPIView(generics.CreateAPIView):
#     serializer_class = EmailOTPSerializer

#     def perform_create(self, serializer):
#         email = serializer.validated_data['email']
#         try:
#             user = User.objects.filter(email=email).get()
#             otp = generate_otp()
#             user.verification_code = otp
#             # Send the OTP code to the provided email
#             subject='OTP Code'
#             message = f'Your OTP code is: {otp}'
#             send_otp_mail.delay(subject=subject, recipient=[email], message=message,)
#             return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
#         except User.DoesNotExist:
#             return Response({'message': 'No staff with this email is registered.'}, status=status.HTTP_400_BAD_REQUEST)





