import json
import random
import requests
from django.conf import settings
import string
import redis
from datetime import datetime

# Redis configuration
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


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
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "mobile_phone": phone_number,
        "message": message,
        "from": "4546",
        "callback_url": "https://api.moneymentor.uz/api/v1/user/sms_callback/",
    }

    url = "https://notify.eskiz.uz/api/message/sms/send"
    response = requests.post(url, headers=headers, data=payload)
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


def check_otp_limit(phone_number, ip_address):
    """
    Telefon raqami va IP manzili uchun OTP cheklovlarini tekshiradi.
    Agar kunlik limit (6) oshib ketmagan bo'lsa True, aks holda False qaytaradi.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Redis keylarini yaratish
    phone_key = f"otp_limit:phone:{phone_number}:{today}"
    ip_key = f"otp_limit:ip:{ip_address}:{today}"

    # Telefon raqami bo'yicha hisoblagich
    phone_count = redis_client.get(phone_key)
    phone_count = int(phone_count) if phone_count else 0

    # IP manzil bo'yicha hisoblagich
    ip_count = redis_client.get(ip_key)
    ip_count = int(ip_count) if ip_count else 0

    # Limit tekshirish (2 martadan ko'p bo'lsa False)
    if phone_count >= 10 or ip_count >= 10:
        return False

    return True


def increment_otp_counter(phone_number, ip_address):
    """
    Telefon raqami va IP manzili uchun OTP hisoblagichlarini oshiradi.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Redis keylarini yaratish
    phone_key = f"otp_limit:phone:{phone_number}:{today}"
    ip_key = f"otp_limit:ip:{ip_address}:{today}"

    # Hisoblagichlarni oshirish
    redis_client.incr(phone_key)
    redis_client.incr(ip_key)

    # Keylar uchun yashash muddatini belgilash (24 soat + 1 soat qo'shimcha)
    expire_seconds = 25 * 60 * 60
    redis_client.expire(phone_key, expire_seconds)
    redis_client.expire(ip_key, expire_seconds)
