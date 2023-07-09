from django.dispatch import receiver

from base.constants import LOGIN, LOGIN_FAILED, LOGOUT
from .models import ActivityLog
from .signals import user_logged_in, user_login_failed, user_logged_out
from .utils import get_client_ip, get_user_location


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print("run")
    message = f"{get_user_location(request)}, {get_client_ip(request)}"
    ActivityLog.objects.create(actor=user, action_type=LOGIN, remarks=message)


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    message = f"{get_user_location(request)}, {get_client_ip(request)}"
    ActivityLog.objects.create(actor=user, action_type=LOGOUT, remarks=message)


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    message = f"{credentials.get('email')},{get_user_location(request)},{get_client_ip(request)}"
    ActivityLog.objects.create(action_type=LOGIN_FAILED, remarks=message)