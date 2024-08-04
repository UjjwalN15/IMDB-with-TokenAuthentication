from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User

def send_otp_for_verification_email(email):
    subject = 'Your Email Verification Email'
    otp = random.randint(100000, 999999)
    message = f'Your OTP for email verification is {otp}. It is only applicable for 5 minutes. Thank you.'
    from_email = settings.EMAIL_HOST
    send_mail(subject, message, from_email, [email])
    user_obj = User.objects.get(email = email)
    user_obj.otp = otp
    user_obj.save()