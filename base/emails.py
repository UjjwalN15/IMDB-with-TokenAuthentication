from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User

def send_otp_for_verification_email(email):
    subject = 'Your Email Verification Captcha'
    otp = random.randint(100000, 999999)
    message = f'Your OTP for email verification is {otp}. It is only applicable for 5 minutes. Thank you.'
    from_email = settings.EMAIL_HOST
    send_mail(subject, message, from_email, [email])
    user_obj = User.objects.get(email = email)
    user_obj.otp = otp
    user_obj.save()
    
def send_email_for_review_added(email, title, ratings):
    subject = 'Thank you for your Review'
    message = f'Your review to the movie {title} is successfully added with the rating {ratings}.'
    from_email = settings.EMAIL_HOST
    send_mail(subject, message, from_email, [email])
    
def send_mail_add_to_watchlist(email, title):
    subject = f'{title} Added to Watchlist'
    message = f'Your movie {title} has been added to your watchlist.'
    from_email = settings.EMAIL_HOST
    send_mail(subject, message, from_email, [email])
    
def send_mail_delete_watchlist(email, title):
    subject = f'{title} removed from Watchlist'
    message = f'Your movie {title} has been removed from your watchlist.'
    from_email = settings.EMAIL_HOST
    send_mail(subject, message, from_email, [email])