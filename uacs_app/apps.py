from django.apps import AppConfig


class UacsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'uacs_app'

    def ready(self):
        from uacs_app import receivers