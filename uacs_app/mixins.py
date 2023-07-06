import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from rest_framework.exceptions import ValidationError

from .models import ActivityLog
from base.constants import UPDATED, CREATED, REVOKED, RESET


class ActivityLogMixin:
    """
    Mixin to track user actions

    :cvar log_message:
        Log message to populate remarks in LogAction

        type --> str

        set this value or override get_log_message

        If not set then, default log message is generated
    """

    log_message = None

    def _get_action_type(self, request) -> str:
        if request.method.upper() == "POST":
            action = request.data.get("action")  # Assuming 'action' is a field in the request data
            if action == REVOKED:
                return REVOKED
            elif action == RESET:
                return RESET
            elif action == UPDATED:
                return UPDATED
        return CREATED

    def _build_log_message(self, request) -> str:
        return f"User: {self._get_user(request)} -- Action Type: {self._get_action_type(request)} -- Path: {request.path} -- Path Name: {request.resolver_match.url_name}"

    def get_log_message(self, request) -> str:
        return self.log_message or self._build_log_message(request)


    @staticmethod
    def _get_user(request):
        return request.user if request.user.is_authenticated else None

    def _write_log(self, request, response):
        actor = self._get_user(request)
    
        data = {
            "actor": actor,
            "action_type": self._get_action_type(request),
        }
        try:
            data["content_type"] = ContentType.objects.get_for_model(
                self.get_queryset().model
            )
            data["content_object"] = self.get_object()
            data["object_id"] = self.get_object().id
        except (AttributeError, ValidationError):
            data["content_type"] = None
        except AssertionError:
            pass

        ActivityLog.objects.create(**data)

    def finalize_response(self, request, *args, **kwargs):
        response = super().finalize_response(request, *args, **kwargs)
        self._write_log(request, response)
        return response