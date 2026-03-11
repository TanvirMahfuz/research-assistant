"""Email helper: send a short summary of the research log via SMTP."""
import smtplib
import ssl
from email.message import EmailMessage
from . import config
import logging

logger = logging.getLogger(__name__)


def send_email(subject: str, body: str, to_addr: str = None) -> bool:
    """Send an email using credentials from config. Returns True on success."""
    to_addr = to_addr or config.EMAIL_USER
    if not all([config.EMAIL_USER, config.EMAIL_PASS]):
        logger.warning("Email credentials not configured; skipping email")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_USER
    msg["To"] = to_addr
    msg.set_content(body)

    # Use Gmail-style SMTP with TLS by default
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(config.EMAIL_USER, config.EMAIL_PASS)
            server.send_message(msg)
        logger.info("Email sent to %s", to_addr)
        return True
    except Exception as exc:
        logger.exception("Failed to send email: %s", exc)
        return False
