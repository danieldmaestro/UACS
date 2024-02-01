from django.core.mail import EmailMessage
from django.conf import settings

from celery import shared_task

@shared_task
def send_otp_mail(subject, recipient, message):    
    msg = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient,
    )
    msg.content_subtype = 'html'
    msg.send()
    return "Done"