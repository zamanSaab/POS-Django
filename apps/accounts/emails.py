from django.conf import settings
from django.core.mail import send_mail


def send_welcome_email(user):
    send_mail(
        subject="Welcome to FRJ-POS",
        message=(
            f"Hi {user.name},\n\n"
            f"Thanks for creating your FRJ-POS account.\n\n"
            f"Start shopping at: {settings.FRONTEND_URL}\n\n"
            f"— The FRJ-POS Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
