from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.core.mail import send_mail
# import uuid
from django.conf import settings

# class MyPasswordResetTokenGenerator(PasswordResetTokenGenerator):
#     def _make_hash_value(selfs,user,timestamp):
#         return (
#             six.text_type(user.pk) + six.text_type(timestamp)
#         )
# pasword_reset_token=MyPasswordResetTokenGenerator()

def send_forget_password_mail(email,token):
    # token=str(uuid.uuid4())
    subject='Your forgot password link is :-'
    message=f'Hi clink on the given link for reset your password http://127.0.0.1:5000/password-reset/{token}/'
    email_from=settings.EMAIL_HOST_USER
    recipient_list=[email]
    send_mail(subject,message,email_from,recipient_list)
    return True
