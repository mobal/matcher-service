from email.message import EmailMessage
from unittest.mock import MagicMock, patch

from app.services.mail_service import MailService
from app.settings import Settings


class TestMailService:
    def test_skips_delivery_when_disabled(self, mail_service: MailService) -> None:
        service_settings = Settings(mail_enabled=False)
        with patch("app.services.mail_service.settings", service_settings):
            result = mail_service.send(
                subject="Subject", body="Body", recipients=["a@test"]
            )

        assert not result

    def test_sends_authenticated_tls_message(self, mail_service: MailService) -> None:
        service_settings = Settings(
            mail_enabled=True,
            mail_host="smtp.test",
            mail_port=587,
            mail_use_tls=True,
            mail_username="user",
            mail_password="password",
            mail_from_name="Matcher Service",
            mail_from_address="from@test",
        )
        smtp = MagicMock()
        smtp.__enter__.return_value = smtp
        sent: list[EmailMessage] = []
        smtp.send_message.side_effect = sent.append
        with (
            patch("app.services.mail_service.settings", service_settings),
            patch(
                "app.services.mail_service.smtplib.SMTP", return_value=smtp
            ) as smtp_factory,
        ):
            result = mail_service.send(
                subject="Subject", body="Body", recipients=["a@test", "b@test"]
            )

        assert result
        smtp_factory.assert_called_once_with("smtp.test", 587)
        smtp.starttls.assert_called_once_with()
        smtp.login.assert_called_once_with("user", "password")
        assert sent[0]["Subject"] == "Subject"
        assert sent[0]["To"] == "a@test, b@test"
        assert sent[0].get_content() == "Body\n"
