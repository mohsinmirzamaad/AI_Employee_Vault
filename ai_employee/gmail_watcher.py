"""Gmail Watcher — monitors Gmail for unread important messages.

Extends BaseWatcher to poll Gmail API and create action files
in /Needs_Action for Claude to process.

Requires:
  - Google Cloud project with Gmail API enabled
  - OAuth2 credentials (credentials.json) from Google Cloud Console
  - First run will open browser for authorization, then saves token.json

Usage:
  uv run python gmail_watcher.py
"""

import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from base_watcher import BaseWatcher
from logger import log_action

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GmailWatcher')

DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
DEV_MODE = os.getenv('DEV_MODE', 'true').lower() == 'true'
VAULT_PATH = os.getenv('VAULT_PATH', '/mnt/c/Users/Mohsin/Desktop/AI_Employee_Vault')

# Paths for Gmail OAuth files (outside vault, never committed)
CREDENTIALS_PATH = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
TOKEN_PATH = os.getenv('GMAIL_TOKEN_PATH', 'token.json')
PROCESSED_IDS_PATH = os.getenv('GMAIL_PROCESSED_IDS', '.gmail_processed_ids.json')

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def _get_gmail_service():
    """Build and return an authenticated Gmail API service."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    token_path = Path(TOKEN_PATH)

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=120)
        self.processed_ids = self._load_processed_ids()
        self.service = None  # Lazy init

    def _load_processed_ids(self) -> set:
        path = Path(PROCESSED_IDS_PATH)
        if path.exists():
            try:
                return set(json.loads(path.read_text()))
            except (json.JSONDecodeError, ValueError):
                return set()
        return set()

    def _save_processed_ids(self):
        Path(PROCESSED_IDS_PATH).write_text(
            json.dumps(list(self.processed_ids), indent=2)
        )

    def _ensure_service(self):
        if self.service is None:
            self.service = _get_gmail_service()

    def check_for_updates(self) -> list:
        if DEV_MODE:
            logger.info('[DEV MODE] Skipping Gmail API call — returning sample data')
            return self._get_sample_emails()

        self._ensure_service()
        try:
            results = self.service.users().messages().list(
                userId='me', q='is:unread is:important', maxResults=10
            ).execute()
        except Exception as e:
            logger.error(f'Gmail API error: {e}')
            return []

        messages = results.get('messages', [])
        new_messages = [m for m in messages if m['id'] not in self.processed_ids]

        if not new_messages:
            logger.info('No new important unread emails')
        else:
            logger.info(f'Found {len(new_messages)} new email(s)')

        return new_messages

    def _get_sample_emails(self) -> list:
        """Return sample email data for DEV_MODE testing."""
        sample_id = 'dev_sample_001'
        if sample_id in self.processed_ids:
            return []
        return [{
            'id': sample_id,
            '_dev_mode': True,
            '_headers': {
                'From': 'client@example.com',
                'Subject': '[DEV] Sample important email',
                'Date': datetime.now(timezone.utc).isoformat(),
            },
            '_snippet': 'This is a sample email for development testing. '
                        'Please review the attached invoice for January.',
        }]

    def create_action_file(self, message) -> Path:
        msg_id = message['id']

        if message.get('_dev_mode'):
            headers = message['_headers']
            snippet = message['_snippet']
        else:
            self._ensure_service()
            msg = self.service.users().messages().get(
                userId='me', id=msg_id
            ).execute()
            header_list = msg.get('payload', {}).get('headers', [])
            headers = {h['name']: h['value'] for h in header_list}
            snippet = msg.get('snippet', '')

        sender = headers.get('From', 'Unknown')
        subject = headers.get('Subject', 'No Subject')
        date = headers.get('Date', datetime.now(timezone.utc).isoformat())
        now = datetime.now(timezone.utc).isoformat()

        content = f"""---
type: email
from: "{sender}"
subject: "{subject}"
received: {now}
original_date: "{date}"
priority: high
status: pending
message_id: "{msg_id}"
---

## Email Content
{snippet}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
"""

        filename = f'EMAIL_{msg_id}.md'
        filepath = self.needs_action / filename

        if DRY_RUN:
            logger.info(f'[DRY RUN] Would create {filename} from {sender}: {subject}')
        else:
            filepath.write_text(content)
            logger.info(f'Created action file: {filename}')

        self.processed_ids.add(msg_id)
        self._save_processed_ids()

        log_action(
            vault_path=self.vault_path,
            action_type='email_fetched',
            actor='gmail_watcher',
            target=filename,
            parameters={
                'from': sender,
                'subject': subject,
                'message_id': msg_id,
            },
            result='dry_run' if DRY_RUN else 'success',
        )

        return filepath


def main():
    mode = 'DRY RUN' if DRY_RUN else 'LIVE'
    dev = ' (DEV MODE)' if DEV_MODE else ''
    logger.info(f'Gmail Watcher starting in {mode}{dev} mode')
    logger.info(f'Vault: {VAULT_PATH}')

    watcher = GmailWatcher(VAULT_PATH)
    watcher.run()


if __name__ == '__main__':
    main()
