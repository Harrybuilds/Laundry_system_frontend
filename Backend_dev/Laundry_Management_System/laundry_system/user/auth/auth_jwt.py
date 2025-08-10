import jwt
from datetime import datetime, timedelta
from django.conf import settings
from random import randint
from django.core.mail import send_mail
from django.core.cache import cache
#import requests


def generate_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def generate_otp(limit=6):
    '''
    '''
    otp = ''.join([str(randint(0, 9)) for _ in range(limit)])
    return otp


def verify_otp(otp, cached_otp):
    if otp == cached_otp:
        return True
    return None


def send_otp_email(otp, email_addresses=None, expires=300):
    '''
    *sends otp to email*
    receives otp, email address(es) and expected expiry time
    setup email adddress(es), sender address, subject and message
    then send the message using django send_mail function
    '''
    if email_addresses is not None and isinstance(email_addresses, (str, tuple, dict)):
        email_addresses = [email_addresses]
    sender_address = 'nonreply@testemail.com'
    subject= 'Your OTP code (do not share with anybody)'
    message = f'Your otp is {otp} and it will expire in {expires / 60} minutes'
    send_mail(subject, message, sender_address, email_addresses)


def get_client_ip(request):
    '''
    *gets the ip adddress of the client*
    extract it from the request.META dictionary
    then renturn the ip address
    '''
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded.split(',')[0] if  x_forwarded else request.META.get('REMOTE_ADDR')
"""
def send_otp_sms(otp, phone, expires=5):
    api_key = 'my_termii_api_key'
    sender_id = 'Laundry'
    message = f'Your OTP is {otp}'
    url = 'https://api.ng.termii.com/api/sms/send'

    payload = {
        'to': phone,
        'from': sender_id,
        'sms': message,
        'type': 'plain',
        'channel': 'generic',
        'api_key': api_key
    }

    response = requests.post(url, json=payload)
    return response.json()
"""