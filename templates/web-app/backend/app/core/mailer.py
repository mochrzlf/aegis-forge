"""Minimal SMTP mailer — stdlib only, no new dependency (ADR-007).

Reset and verification links are handed to the local Mailpit relay from
docker-compose. Two rules are load-bearing here:

* Sending runs off the event loop via ``asyncio.to_thread``, so a slow or
  unreachable relay can never stall an auth request.
* Delivery problems are logged and swallowed. The caller still answers success,
  because a failed-to-send reset link must not become an error that tells an
  attacker which addresses are registered (the request endpoint is unauthenticated).

PII discipline: the recipient address and the link itself never reach the logs.
"""
import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str) -> None:
    if not settings.SMTP_HOST:
        # Delivery disabled (no relay configured): nothing is sent and nothing
        # is echoed into the API response either.
        logger.info("smtp disabled — message dropped (subject=%s)", subject)
        return
    try:
        await asyncio.to_thread(_send_sync, to, subject, body)
    except Exception:
        # Deliberately broad: see module docstring — a mail fault is not a 500.
        logger.exception("smtp delivery failed (subject=%s)", subject)


def _send_sync(to: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
        smtp.send_message(message)
