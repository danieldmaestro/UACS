from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from base.constants import UPDATED, CREATED, REVOKED, RESET, LOGIN, LOGIN_FAILED, LOGOUT, FAILED
from .models import Staff, StaffPermission, ServiceProvider, ActivityLog, Admin, SecurityLog
from uacs_app import signals

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    """Custom login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def get_token(self, user):
        refresh_token = RefreshToken.for_user(user)
        access = str(refresh_token.access_token)
        refresh = str(refresh_token)
        return access, refresh

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        admin = Admin.objects.get(user__email=email)
        request = self.context.get('request')
        
        if not admin or not admin.user.check_password(password):
            credentials = {'email': email}
            signals.user_login_failed.send(sender=User, credentials=credentials, request=request, status=FAILED)
            raise serializers.ValidationError('Invalid login credentials or not a verified user')
        
        access, refresh = self.get_token(admin.user)
        
        payload = {
            'first_name': admin.first_name,
            'last_name': admin.last_name,
            'profile_picture': request.build_absolute_uri(admin.profile_picture.url) if admin.profile_picture else "empty",
            'email': email,
            'access': access,
            'refresh': refresh,
        }
        signals.user_logged_in.send(sender=User, request=request, user=admin.user)
        return payload
    

class LogoutSerializer(serializers.Serializer):
    """Logout serializer"""

    refresh = serializers.CharField(write_only=True)

    def validate(self, attrs):
        refresh = attrs.get("refresh")
        try:
            token = RefreshToken(refresh)
            return {'refresh': refresh}
        except TokenError:
            raise serializers.ValidationError('Invalid Refresh Token')    


class StaffPermissionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="uacs:staff_permission_detail", read_only=True)
    sp_list = serializers.PrimaryKeyRelatedField(queryset=ServiceProvider.objects.all(), many=True, write_only=True)
    staff_list = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all(), many=True, write_only=True)
    staff = serializers.HyperlinkedRelatedField(view_name="uacs:staff_detail", read_only=True)
    service_provider = serializers.HyperlinkedRelatedField(view_name="uacs:sp_detail", read_only=True)
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = StaffPermission
        fields = ['id', 'url', 'name','staff', 'service_provider', 'staff_list', 'sp_list', 'is_permitted']
        read_only_fields = ('is_permitted', 'name')

    def get_name(self, obj) -> str:
        return obj.service_provider.name


class PermissionUpdateSerializer(serializers.Serializer):
    
    permission_list = serializers.PrimaryKeyRelatedField(queryset=StaffPermission.objects.all(), many=True, write_only=True)

    def validate(self, attrs):
        return super().validate(attrs)


class StaffSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="uacs:staff_detail", read_only=True)
    full_designation = serializers.SerializerMethodField()
    tribe = serializers.CharField(source="tribe.name", read_only=True)
    squad = serializers.CharField(source="squad.name", read_only=True)
    designation = serializers.CharField(source="designation.name", read_only=True)
    tribe_name = serializers.CharField(write_only=True)
    squad_name = serializers.CharField(write_only=True)
    designation_name = serializers.CharField(write_only=True)
    reset_url = serializers.SerializerMethodField()
    revoke_url = serializers.SerializerMethodField()
    permission_update_url = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = ['id', 'url', 'email', 'first_name', 'last_name', 'phone_number', 'tribe', 'squad', 'role', 
                  'designation', 'full_designation', 'tribe_name', 'squad_name', 'designation_name', 
                  'reset_url', 'revoke_url', 'permissions', 'profile_picture', 'permission_update_url',]
    
    def get_full_designation(self,obj) -> str:
        return f"{obj.role}, {obj.designation}"
    
    def get_reset_url(self, obj) -> str:
        request = self.context.get('request')
        if request is not None:
            return reverse('uacs:reset', args=[obj.id], request=request)
        return None

    def get_revoke_url(self, obj) -> str:
        request = self.context.get('request')
        if request is not None:
            return reverse('uacs:revoke', args=[obj.id], request=request)
        return None
    
    def get_permissions(self, obj) -> str:
        permissions = obj.sp_permissions.all()
        request = self.context.get('request')
        if request is not None:
            return StaffPermissionSerializer(permissions, many=True, context={'request': request}).data
        return None
    
    def get_permission_update_url(self,obj) -> str:
        request = self.context.get('request')
        if request is not None:
            return reverse('uacs:staff_permission_update', request=request)
        return None


class ServiceProviderSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="uacs:sp_detail", read_only=True)
    slug = serializers.SlugField(read_only=True)
    picture = serializers.ImageField()
    test_picture_url = serializers.SerializerMethodField()
    staffs_with_permission = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    toggle_status_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceProvider
        fields = ['id', 'url', 'picture', 'test_picture_url', 'name', 'date', 'website_url', 'slug', 'toggle_status_url', 'is_active', 'staffs_with_permission',]

    def get_staffs_with_permission(self, obj) -> dict:
        staffs = Staff.active_objects.filter(sp_permissions__service_provider=obj,
                                    sp_permissions__is_permitted=True)
        request = self.context.get('request')
        if request is not None:
            return StaffSerializer(staffs, many=True, context={'request': request}).data
        return None
    
    def get_test_picture_url(self, obj) -> str:
        if obj.name == 'ECN':
            return 'https://uacs.afex.dev/uploads/sp_images/ecn46b0c7b1-114b-4c09-9f6a-9ae1405bebeb.png'
        elif obj.name == "Commodity Grading System":
            return "https://uacs.afex.dev/uploads/sp_images/cgs-logo4444fac0-7b6b-4eba-b2bf-76cf659d6d9e.png"
        else:
            return 'https://uacs.afex.dev/uploads/sp_images/workbench27710ebe-a291-40f6-acc6-3a2a9b164575.webp'

    def get_date(self,obj) -> str:
        return obj.created_date.date()  

    def get_toggle_status_url(self, obj) -> str:
        request = self.context.get('request')
        if request is not None:
            return reverse('uacs:sp_toggle_status', args=[obj.id], request=request)
        return None


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    activity = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'actor', 'actor_name', 'action_time', 'date', 'time', 'status', 'activity']


    def get_activity(self, obj) -> str:
        if obj.action_type == UPDATED:
            return f"{obj.action_type} {obj.content_object.staff.full_name()}'s permission for {obj.content_object.service_provider.name}"
        elif obj.action_type == REVOKED:
            return f"{obj.action_type} access for {obj.content_object.full_name()}"
        elif obj.action_type == RESET:
            return f"{obj.action_type} access for {obj.content_object.full_name()}"
        elif obj.action_type == CREATED:
            return f"{obj.action_type} a service provider, {obj.content_object.name}"
        
    def get_date(self, obj) -> str:
        date = obj.action_time
        formatted_date = date.strftime('%dth %B %Y')
        return formatted_date
    
    def get_time(self, obj) -> str:
        date = obj.action_time
        formatted_time = date.strftime('%I:%M %p')
        return formatted_time
    
    def get_actor_name(self, obj) -> str:
        if hasattr(obj.actor, 'admin'):
            return obj.actor.admin.full_name()
        return obj.actor.email
    
    
class SecurityLogSerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    ip_address = serializers.SerializerMethodField()
    service_provider = serializers.SerializerMethodField()

    class Meta:
        model = SecurityLog
        fields = ['id', 'date', 'time', 'status', 'activity', 'location', 'ip_address', 'service_provider']

    def get_activity(self, obj) -> str:
        if obj.action_type == LOGIN:
            return f"Attempted login by {obj.actor.email}"
        elif obj.action_type == LOGIN_FAILED:
            remark_list = [item.strip() for item in obj.remarks.split(",")]
            return f"Attempted login by {remark_list[0]}"
        elif obj.action_type == LOGOUT:
            return f"{obj.actor.email} successfully logged out."
        
    def get_date(self, obj) -> str:
        date = obj.action_time
        formatted_date = date.strftime('%b. %d, %Y')
        return formatted_date
        
    def get_time(self, obj) -> str:
        date = obj.action_time
        formatted_time = date.strftime('%I:%M %p')
        return formatted_time.lower()
    
    def get_location(self, obj) -> str:
        return obj.location
    
    def get_ip_address(self, obj) -> str:
        return f"IP {obj.ip_address}"
    
    def get_service_provider(self,obj) -> str:
        return "UACS"
        

class EmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6, write_only=True)
    email = serializers.EmailField(write_only=True)


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = User
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        return attrs







