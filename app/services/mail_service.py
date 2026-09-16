import smtplib
from email.message import EmailMessage

from app.settings import settings


class MailService:
    def send(
        self, *, subject: str, body: str, recipients: list[str] | None = None
    ) -> bool:
        addresses = (
            recipients if recipients is not None else settings.notification_recipients
        )
        if not settings.mail_enabled or not addresses:
            return False

        message = EmailMessage()
        message["From"] = f"{settings.mail_from_name} <{settings.mail_from_address}>"
        message["To"] = ", ".join(addresses)
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(settings.mail_host, settings.mail_port) as client:
            if settings.mail_use_tls:
                client.starttls()
            if settings.mail_username and settings.mail_password:
                client.login(settings.mail_username, settings.mail_password)
            client.send_message(message)
        return True
