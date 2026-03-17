import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from fastapi import Depends

from flux_watch_api.core.config import AppConfig

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, config: AppConfig = Depends()):
        self.sender_email = config.FWES_SENDER_MAIL
        self.sender_password = config.FWES_SENDER_PASS

        if not self.sender_email or not self.sender_password:
            raise ValueError("email and app password must be provided")

        self.smtp_server = config.FWES_SMTP_SERVER
        self.smtp_port = config.FWES_SMTP_PORT  # ssl port
        self.config = config
        self.base_path: Path = Path(__file__).parent

    def _generate_content(self, template_path: str, **kwargs):
        content_template = self.base_path.joinpath(template_path)

        with content_template.open(encoding="utf-8") as f:
            content = f.read()
        return content.format(**kwargs)

    def _generate_email(self, template_path: str, **kwargs):
        return self._generate_content(template_path, **kwargs)

    def send_email(self, to_emails: list[str] | str, subject: str, template_path: str, **kwargs):
        if isinstance(to_emails, str):
            to_emails = [to_emails]

        body = self._generate_email(template_path, **kwargs)

        # Create MIME message
        message = MIMEMultipart("alternative")
        message["From"] = self.sender_email
        message["To"] = ", ".join(to_emails)
        message["Subject"] = subject

        message.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_emails, message.as_string())
            logger.info(f"Email sent successfully to {to_emails}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
