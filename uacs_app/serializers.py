from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Staff, StaffPermission, ServiceProvider

class StaffSerializer(serializers.ModelSerializer):
    pass