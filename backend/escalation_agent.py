import os, requests
from dotenv import load_dotenv

load_dotenv()

# Slack
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')

# SendGrid
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
ALERT_EMAIL_TO = os.getenv('ALERT_EMAIL_TO')
FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')  # must be verified sender

def send_slack(message: str):
    if not SLACK_WEBHOOK:
        return {'ok': False, 'reason': 'no_webhook'}
    try:
        r = requests.post(SLACK_WEBHOOK, json={'text': message}, timeout=10)
        return {'ok': r.status_code == 200, 'status_code': r.status_code, 'text': r.text}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def send_email(to_addr: str, subject: str, body: str):
    to_addr = to_addr or ALERT_EMAIL_TO
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        return {'ok': False, 'reason': 'no_sendgrid_config'}
    try:
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "personalizations": [
                {"to": [{"email": to_addr}]}
            ],
            "from": {"email": FROM_EMAIL},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}]
        }

        r = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers=headers,
            json=data,
            timeout=10
        )

        return {'ok': r.status_code == 202, 'status_code': r.status_code, 'text': r.text}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
