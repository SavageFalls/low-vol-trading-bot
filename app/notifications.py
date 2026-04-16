from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

import requests

from app.config import Settings


class Notifier:
    def __init__(self, settings: Settings):
        self.settings = settings

    def notify(self, message: str):
        self._notify_discord(message)
        self._notify_email(message)

    def _notify_discord(self, message: str):
        if not self.settings.discord_webhook_url:
            return
        requests.post(self.settings.discord_webhook_url, json={"content": message[:1900]}, timeout=20)

    def _notify_email(self, message: str):
        if not all(
            [
                self.settings.smtp_host,
                self.settings.smtp_user,
                self.settings.smtp_password,
                self.settings.email_to,
                self.settings.email_from,
            ]
        ):
            return

        msg = MIMEText(message)
        msg["Subject"] = "Daily Hedge Fund Briefing"
        msg["From"] = self.settings.email_from
        msg["To"] = self.settings.email_to

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
            server.starttls()
            server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.sendmail(self.settings.email_from, [self.settings.email_to], msg.as_string())
