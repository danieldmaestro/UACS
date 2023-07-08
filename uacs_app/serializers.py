from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from rest_framework import serializers
from rest_framework.reverse import reverse

User = get_user_model()

from .models import Staff, StaffPermission, ServiceProvider, ActivityLog



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
        read_only_fields =('is_permitted', 'name')

    def get_name(self, obj):
        return obj.service_provider.name



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
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = ['id', 'url', 'email', 'first_name', 'last_name', 'phone_number', 'tribe', 'squad', 'role', 
                  'designation', 'full_designation', 'tribe_name', 'squad_name', 'designation_name', 
                  'reset_url', 'revoke_url', 'permissions']

    
    def get_full_designation(self,obj) -> str:
        return f"{obj.role}, {obj.designation}"
    
    def get_reset_url(self, obj):
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


class ServiceProviderSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="uacs:sp_detail", read_only=True)
    slug = serializers.SlugField(read_only=True)
    picture = serializers.ImageField(read_only=True)
    class Meta:
        model = ServiceProvider
        fields = ['id', 'url', 'picture', 'name', 'website_url', 'slug', ]


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    activity = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'actor', 'action_time', 'date', 'time', 'status', 'activity']
        extra_kwargs = {'url': {'view_name': 'uacs:activitylog-detail'}}


    def get_activity(self, obj) -> str:
        if obj.action_type == 'UPDATED':
            return f"{obj.action_type} {obj.content_object.staff.full_name()}'s permission for {obj.content_object.service_provider.name}"
        elif obj.action_type == 'REVOKED':
            return f"{obj.action_type} access for {obj.content_object.full_name()}"
        elif obj.action_type == 'RESET':
            return f"{obj.action_type} access for {obj.content_object.full_name()}"
        elif obj.action_type == 'LOGIN':
            return f"Attempted login by {obj.content_object.email}"
        elif obj.action_type == 'CREATED':
            return f"{obj.action_type} a service provider, {obj.content_object.name}"
        
    def get_date(self, obj) -> str:
        return obj.action_time.date()
    
    def get_time(self, obj) -> str:
        return obj.action_time.time()
        

class EmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6, write_only=True)
    email = serializers.EmailField(write_only=True)


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        return attrs






