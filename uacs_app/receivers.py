from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver

from .models import SecurityLog, ActivityLog
from .signals import user_logged_in, user_login_failed, user_logged_out, permission_updated
from .utils import get_client_ip, get_user_location

from base.constants import LOGIN, LOGIN_FAILED, LOGOUT


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    location = get_user_location(request) 
    ip_address = get_client_ip(request)
    SecurityLog.objects.create(actor=user, action_type=LOGIN, location=location, ip_address=ip_address)

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    location = get_user_location(request) 
    ip_address = get_client_ip(request)
    SecurityLog.objects.create(actor=user, action_type=LOGOUT, location=location, ip_address=ip_address)

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    message = credentials['email']
    status = kwargs.pop("status")
    location = get_user_location(request) 
    ip_address = get_client_ip(request)
    SecurityLog.objects.create(action_type=LOGIN_FAILED, remarks=message, status=status, location=location, ip_address=ip_address)

@receiver(permission_updated)
def log_permission_updated(sender, user, **kwargs):
    message = f"Updated permission for this staff"
    action_type = kwargs.pop("action_type")
    content_object = kwargs.pop("content_object")
    content_type =  ContentType.objects.get_for_model(sender)
    ActivityLog.objects.create(actor=user, action_type=action_type, content_type=content_type, remarks=message, 
                content_object=content_object, object_id=content_object.id)
    

