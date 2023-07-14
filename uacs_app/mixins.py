import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from rest_framework.exceptions import ValidationError

from .models import ActivityLog
from base.constants import UPDATED, CREATED, REVOKED, RESET, LOGIN, LOGOUT, LOGIN_FAILED, SUCCESS, FAILED


class ActivityLogMixin:
    """
    Mixin to track user actions
    :cvar log_message:
        Log message to populate remarks in LogAction
        If not set then, default log message is generated
    """

    log_message = None

    def _get_action_type(self, request) -> str:
        action = request.data.get("action")  # Assuming 'action' is a field in the request data
        if request.method.upper() == "PATCH":
            if action == REVOKED:
                return REVOKED
            elif action == RESET:
                return RESET
            
        elif request.method.upper() == "POST":
            return CREATED

    def _build_log_message(self, request) -> str:
        return f"User: {self._get_user(request)} -- Action Type: {self._get_action_type(request)} -- Path: {request.path} -- Path Name: {request.resolver_match.url_name}"

    def get_log_message(self, request) -> str:
        return self.log_message or self._build_log_message(request)


    @staticmethod
    def _get_user(request):
        return request.user if request.user.is_authenticated else None

    def _write_log(self, request, response):
        status = SUCCESS if response.status_code < 400 else FAILED
        actor = self._get_user(request)
    
        data = {
            "actor": actor,
            "action_type": self._get_action_type(request),
            "status": status,
            "remarks": self.get_log_message(request), 
        }
        try:
            data["content_type"] = ContentType.objects.get_for_model(
                self.get_queryset().model
            )
            if data['action_type'] == CREATED:
                data["content_object"] = self.created_sp
                data["object_id"] = self.created_sp.id
            else:
                data["content_object"] = self.get_object()
                data["object_id"] = self.get_object().id
        except Exception as e:
            data["content_type"] = None
            print("lmao", e)

        ActivityLog.objects.create(**data)

    def finalize_response(self, request, *args, **kwargs):
        response = super().finalize_response(request, *args, **kwargs)
        self._write_log(request, response)
        return response