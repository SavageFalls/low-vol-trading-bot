from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

import requests

from app.config import AppConfig


class Notifier:
    def __init__(self, config: AppConfig):
        self.config = config

    def send_discord(self, message: str) -> None:
        if not self.config.discord_webhook_url:
            return
        requests.post(self.config.discord_webhook_url, json={"content": message[:1900]}, timeout=15)

    def send_email(self, subject: str, body: str) -> None:
        if not all(
            [
                self.config.smtp_host,
                self.config.smtp_user,
                self.config.smtp_password,
                self.config.email_from,
                self.config.email_to,
            ]
        ):
            return

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.config.email_from
        msg["To"] = self.config.email_to

        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
            server.starttls()
            server.login(self.config.smtp_user, self.config.smtp_password)
            server.sendmail(self.config.email_from, [self.config.email_to], msg.as_string())
