import logging
import os
import smtplib
from email.message import EmailMessage

log = logging.getLogger(__name__)


def send_alert(email: str, value: float, station: str, unsubscribe_token: str):
    subject = f"Smog alert: PM2.5 {value:.0f} µg/m³ near you"
    front = os.getenv("FRONTEND_URL", "http://localhost:3000")
    body = (
        f"PM2.5 at {station} is {value:.1f} µg/m³ right now.\n\n"
        f"Maybe keep the windows closed for a while.\n\n"
        f"Unsubscribe: {front}/alerts?unsubscribe={unsubscribe_token}\n"
    )

    host = os.getenv("SMTP_HOST")
    if not host:
        log.info("no SMTP_HOST, alert for %s: %s", email, subject)
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.getenv("SMTP_FROM", "smog@localhost")
    msg["To"] = email
    msg.set_content(body)

    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as s:
        s.starttls()
        user = os.getenv("SMTP_USER")
        if user:
            s.login(user, os.getenv("SMTP_PASSWORD", ""))
        s.send_message(msg)
    return True
