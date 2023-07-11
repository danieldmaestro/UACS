import random
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from . import signals
from accounts.models import User
from base.constants import UPDATED, CREATED, REVOKED, RESET, LOGIN, LOGOUT, LOGIN_FAILED, SUCCESS, FAILED
from .mixins import ActivityLogMixin
from .models import ActivityLog, Staff, Tribe, Squad, Designation, ServiceProvider, StaffPermission, SecurityLog
from .serializers import (StaffSerializer,ServiceProviderSerializer, StaffPermissionSerializer,
                            ActivityLogSerializer, EmailOTPSerializer, ResetPasswordSerializer,
                            VerifyOTPSerializer, LoginSerializer, LogoutSerializer, SecurityLogSerializer,
                            PermissionUpdateSerializer)
from .signals import permission_updated
from .tasks import send_otp_mail
from .utils import create_permissions

# Create your views here.

def generate_otp():
    # Generate a random 6-digit OTP code
    return str(random.randint(100000, 999999))

class LoginAPIView(TokenObtainPairView):
    """Endpoint to get authenticate user"""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        request.data['action'] = LOGIN
        return super().post(request, *args, **kwargs)
    

class LogoutAPIView(generics.GenericAPIView):
    """Endpoint to unauthenticate the authenticated user and blacklist access token"""
    serializer_class = LogoutSerializer
    
    def post(self, request, *args, **kwargs):
        request.data['action'] = LOGOUT
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data['refresh']
        token = RefreshToken(refresh)
        token.blacklist()
        signals.user_logged_out.send(sender=User, request=self.request, user=self.request.user)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)     
        

class StaffListCreateAPIView(generics.ListCreateAPIView):
    """Endpoint to create and new Staff and get list of staffs in the database"""
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    queryset = Staff.objects.all()

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search_query')
        if search_query:
            # Apply search filter using Q objects
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        return queryset
    
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
    """Endpoint to get individual staff information"""
    serializer_class = StaffSerializer
    queryset = Staff.objects.all()
    permission_classes = [IsAuthenticated]


class StaffAccessResetAPIView(ActivityLogMixin, generics.UpdateAPIView):
    """Endpoint to restore staff active and allow all previously granted permissions"""
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def patch(self, request, *args, **kwargs):
        request.data['action'] = RESET
        instance = self.get_object()
        if not instance.is_active:
            instance.is_active = True
            instance.save()
            return Response({'message': 'Staff access has been restored successfully.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Staff access is not revoked.'}, status=status.HTTP_400_BAD_REQUEST)
        
    
class StaffAccessRevokeAPIView(ActivityLogMixin, generics.UpdateAPIView):
    """Endpoint to revoke all staff access permissions and make staff inactive"""
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def patch(self, request, *args, **kwargs):
        request.data['action'] = REVOKED
        instance = self.get_object()
        if instance.is_active:
            instance.is_active = False
            instance.save()
            return Response({'message': 'Staff access has been revoked successfully.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Staff access is already revoked.'}, status=status.HTTP_400_BAD_REQUEST)
        

class ServiceProviderCreateAPIView(ActivityLogMixin, generics.CreateAPIView):
    """"""
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]
    queryset = ServiceProvider.objects.all()

    def perform_create(self, serializer):
        service_provider = serializer.save()
        self.created_sp = service_provider
        for staff in Staff.objects.all():
            StaffPermission.objects.create(staff=staff, service_provider=service_provider)

        return Response({'message': 'Service Provider created succesfully'}, status=status.HTTP_201_CREATED)


class ServiceProviderListAPIView(generics.ListAPIView):
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]
    queryset = ServiceProvider.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search_query')
        if search_query:
            # Apply search filter using Q objects
            queryset = queryset.filter(
                Q(name__icontains=search_query)
            )
        return queryset
    
    
class ServiceProviderToggleStatusAPIView(ActivityLogMixin, generics.UpdateAPIView):
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]
    queryset = ServiceProvider.objects.all()

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()
        if instance.is_active:
            return Response({'message': f'{instance.name} status is set to Active'})
        return Response({'message': f'{instance.name} status is set to Inactive'})
    
        
class ServiceProviderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ServiceProviderSerializer
    queryset = ServiceProvider.objects.all()
    permission_classes = [IsAuthenticated]


class ActivityLogListAPIView(generics.ListAPIView):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]


class ActivityLogDetailAPIView(generics.RetrieveAPIView):

    """Endpoint for list of Security Logs"""
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]


class SecurityLogListAPIView(generics.ListAPIView):
    queryset = SecurityLog.objects.all()
    serializer_class = SecurityLogSerializer
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
    

class DashboardCountAPIView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        inactive_sp = ServiceProvider.objects.filter(is_active=False).count()
        active_staff = Staff.objects.filter(is_active=True).count()

        response = {'inactive_sps': inactive_sp,
                    'staff_with_access': active_staff}
        return Response(response, status=status.HTTP_200_OK)


class StaffPermissionSetAPIView(generics.GenericAPIView):

    serializer_class = StaffPermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff_list = serializer.validated_data.pop("staff_list")
        sp_list = serializer.validated_data.pop("sp_list")

        for staff in staff_list:
            staff_permissions = staff.sp_permissions.filter(service_provider__in=sp_list)

            for permission in staff_permissions:
                permission.is_permitted = True
                permission.save()
                permission_updated.send(sender=StaffPermission, user=user, action_type=UPDATED, content_object=permission)
        return Response({'message': 'Permission granted for selected staff and service providers'}, status=status.HTTP_201_CREATED)


class StaffPermissionDetailAPIView(generics.RetrieveAPIView):
    queryset = StaffPermission.objects.all()
    serializer_class = StaffPermissionSerializer
    lookup_field = 'pk'


class StaffPermissionListAPIView(generics.ListAPIView):
    serializer_class = StaffPermissionSerializer
    queryset = StaffPermission.objects.all()

    
class StaffPermissionUpdateAPIView(generics.GenericAPIView):
    serializer_class = PermissionUpdateSerializer
    queryset = StaffPermission.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permission_list = serializer.validated_data.pop("permission_list")
        permission_ids = [obj.pk for obj in permission_list]
        staff = permission_list[0].staff
        staff_permissions = staff.sp_permissions.all()

        if not staff_permissions.filter(pk__in=permission_ids).count() == len(permission_ids):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        perm_true = staff_permissions.filter(pk__in=permission_ids)
        perm_false = staff_permissions.exclude(pk__in=permission_ids)

        for perm in perm_true:
            if perm.is_permitted == False:
                perm.is_permitted = True
                perm.save()
                permission_updated.send(sender=StaffPermission, user=user, action_type=UPDATED, content_object=perm)
                print("true loop ran")

        for perm in perm_false:
            if perm.is_permitted == True:
                perm.is_permitted = False
                perm.save()
                permission_updated.send(sender=StaffPermission, user=user, action_type=UPDATED, content_object=perm)
                print("false loop ran")
                

        # staff_permissions.filter(pk__in=permission_ids).values_list("is_permitted", flat=True).update(is_permitted=True)
        # staff_permissions.exclude(pk__in=permission_ids).values_list("is_permitted", flat=True).update(is_permitted=False)
        return Response({'message': f'Permissions for {staff.full_name()} updated successfully.'}, status=status.HTTP_201_CREATED)


