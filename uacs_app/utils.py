import os
import requests

from dotenv import load_dotenv

from .models import ServiceProvider, StaffPermission

load_dotenv()

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return (
        x_forwarded_for.split(",")[0]
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR")
    )

def get_user_location(request):
    ip = get_client_ip(request)
    response = requests.get(f"http://api.ipstack.com/{ip}?access_key={os.environ.get('API_KEY')}")
    if response.status_code == 200:
        data = response.json()
        if data['success'] == True:
            location = f"{data['city']}, {data['country_name']}"
            return location
    return None

def create_permissions(staff):
    for sp_obj in ServiceProvider.objects.all():
        StaffPermission.objects.create(staff=staff, service_provider=sp_obj)