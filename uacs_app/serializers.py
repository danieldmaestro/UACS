from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from rest_framework import serializers
from rest_framework.reverse import reverse

User = get_user_model()

from .models import Staff, StaffPermission, ServiceProvider, ActivityLog

class StaffSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="uacs:staff_detail", read_only=True)
    full_designation = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = ['id', 'url', 'email', 'first_name', 'last_name', 'phone_number', 'tribe', 'squad', 'designation', 'full_designation']

    
    def get_full_designation(self,obj) -> str:
        return f"{obj.role}, {obj.designation}"



class ServiceProviderSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="uacs:service_provider_detail", read_only=True)
    class Meta:
        model = ServiceProvider
        fields = ['id', 'url', 'picture', 'website_url', 'slug',  ]


class StaffPermissionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="uacs:staff_permision_detail", read_only=True)
    class Meta:
        model = StaffPermission
        fields = ['id', 'url', 'staff', 'service_provider', 'is_permitted']


class ActivityLogSerializer(serializers.HyperlinkedModelSerializer):
    actor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    activity = serializers.SerializerMethodField()
    date = serializers.DateField(source='action_time.date', read_only=True)
    time = serializers.TimeField(source='action_time.time', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['url', 'id', 'actor', 'action_type', 'action_time', 'data', 'date', 'time', 'activity']
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
        

class EmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6, write_only=True)


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






