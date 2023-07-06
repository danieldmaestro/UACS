import os
import requests

from dotenv import load_dotenv

load_dotenv()

def get_user_location(request):
    ip = request.META.get('REMOTE_ADDR')
    response = requests.get(f"http://api.ipstack.com/{ip}?access_key={os.environ.get('API_KEY')}")
    if response.status_code == 200:
        data = response.json()
        location = f"{data['city']}, {data['country_name']}"
        return location
    return None

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return (
        x_forwarded_for.split(",")[0]
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR")
    )