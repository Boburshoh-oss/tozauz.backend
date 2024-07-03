import json
import random
import requests
from django.conf import settings
import string
import redis

# Redis configuration
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

def generate_random_password(length=6):
    """Generate a random password (OTP)"""
    characters = string.digits
    return "".join(random.choice(characters) for i in range(length))

def send_sms(phone_number, message):
    """Send SMS using Eskiz API"""
    token = get_token_from_redis()
    if token is None:
        token = eskiz_login()
        save_token_to_redis(token)
    print(token)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "mobile_phone": phone_number,
        "message": message,
        "from": "4546",
        "callback_url": "https://api.moneymentor.uz/api/v1/user/sms_callback/",
    }

    url = "https://notify.eskiz.uz/api/message/sms/send"
    response = requests.post(url, headers=headers, data=payload)
    print(response.json())
    if response.status_code != 200:
        # If the token is expired, refresh it
        token = eskiz_refresh_token()
        if token:
            save_token_to_redis(token)
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(url, headers=headers, data=payload)
    return response


def eskiz_login():
    """Obtain token from Eskiz API"""
    url = "https://notify.eskiz.uz/api/auth/login"
    payload = {"email": settings.ESKIZ_EMAIL, "password": settings.ESKIZ_PASSWORD}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json().get("data").get("token")
    else:
        # Handle error
        return None


def eskiz_refresh_token():
    """Refresh expired token"""
    url = "https://notify.eskiz.uz/api/auth/refresh"
    headers = {"Authorization": f"Bearer {get_token_from_redis()}"}
    response = requests.patch(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data").get("token")
    else:
        return None


def save_token_to_redis(token):
    """Save token to Redis"""
    token_data = json.dumps({"token": token})
    redis_client.setex("eskiz_token", 2592000, token_data)


def get_token_from_redis():
    """Get token from Redis"""
    token_data = redis_client.get("eskiz_token")
    if token_data:
        token = json.loads(token_data).get("token")
        return token
    else:
        return None
