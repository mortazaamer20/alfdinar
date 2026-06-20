"""Minimal OTPIQ client for sending WhatsApp/SMS messages.

Uses only the Python standard library (no extra dependency). Sending is a
no-op that returns ``(False, reason)`` when no API key is configured, so the
rest of the app keeps working in development.

OTPIQ contract (custom free-text message), per https://docs.otpiq.com :
    POST {base}/api/sms/send
    Authorization: Bearer <API_KEY>
    {
        "phoneNumber": "9647xxxxxxxxx",   # country code, no leading +/00
        "smsType": "custom",
        "message": "...",
        "provider": "whatsapp"             # whatsapp | sms | auto
    }
If OTPIQ changes field names, adjust _build_payload below — it is the single
place that defines the request body.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

SEND_PATH = '/api/sms/send'


def normalize_phone(phone):
    """Convert a local Iraqi number to OTPIQ's E.164-without-plus format.

    07XX XXX XXXX -> 9647XXXXXXXXX. Numbers already in country-code form are
    returned digits-only.
    """
    digits = ''.join(ch for ch in str(phone) if ch.isdigit())
    if digits.startswith('00'):
        digits = digits[2:]
    if digits.startswith('964'):
        return digits
    if digits.startswith('0'):
        return '964' + digits[1:]
    return digits


def _build_payload(phone_number, message):
    return {
        'phoneNumber': phone_number,
        'smsType': 'custom',
        'message': message,
        'provider': getattr(settings, 'OTPIQ_PROVIDER', 'whatsapp'),
    }


def send_message(phone, message, timeout=20):
    """Send ``message`` to ``phone`` via OTPIQ.

    Returns a tuple ``(ok: bool, info: str)``. Never raises — network/HTTP
    errors are caught and reported so callers (e.g. the cron command) can keep
    going through the rest of the recipients.
    """
    api_key = getattr(settings, 'OTPIQ_API_KEY', '')
    if not api_key:
        return False, 'OTPIQ_API_KEY غير مُعرّف'

    url = settings.OTPIQ_BASE_URL.rstrip('/') + SEND_PATH
    payload = _build_payload(normalize_phone(phone), message)
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {api_key}')
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', 'replace')
            return True, body
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', 'replace') if exc.fp else ''
        logger.warning('OTPIQ HTTP %s for %s: %s', exc.code, phone, detail)
        return False, f'HTTP {exc.code}: {detail}'
    except Exception as exc:  # noqa: BLE001 - report any transport error
        logger.warning('OTPIQ send failed for %s: %s', phone, exc)
        return False, str(exc)
