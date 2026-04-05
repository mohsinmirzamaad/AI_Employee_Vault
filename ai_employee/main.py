"""AI Employee — Main Entry Point.

Starts the orchestrator which manages all watcher processes.
Loads environment from .env, validates vault structure, and launches watchers.

Usage:
  uv run python main.py
  uv run python main.py --dry-run
  uv run python main.py --vault-path /path/to/vault
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Load .env before anything else
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, rely on env vars

from logger import log_action


REQUIRED_FOLDERS = [
    'Inbox', 'Needs_Action', 'Plans', 'Pending_Approval',
    'Approved', 'Rejected', 'Done', 'Logs',
]


def validate_vault(vault_path: Path) -> bool:
    """Ensure all required vault folders exist, creating any missing ones."""
    logger = logging.getLogger('main')
    all_ok = True
    for folder in REQUIRED_FOLDERS:
        folder_path = vault_path / folder
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f'Created missing folder: {folder}')
        all_ok = all_ok and folder_path.is_dir()
    return all_ok


def main():
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument(
        '--vault-path',
        default=os.getenv('VAULT_PATH', '/mnt/c/Users/Mohsin/Desktop/AI_Employee_Vault'),
        help='Path to the Obsidian vault',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=None,
        help='Override DRY_RUN mode (prevents real actions)',
    )
    args = parser.parse_args()

    if args.dry_run is True:
        os.environ['DRY_RUN'] = 'true'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger('main')

    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        logger.error(f'Vault path does not exist: {vault_path}')
        sys.exit(1)

    logger.info(f'AI Employee starting...')
    logger.info(f'Vault: {vault_path}')

    validate_vault(vault_path)

    log_action(
        vault_path=vault_path,
        action_type='system_startup',
        actor='main',
        target='ai_employee',
        parameters={
            'vault_path': str(vault_path),
            'dry_run': os.getenv('DRY_RUN', 'true'),
            'dev_mode': os.getenv('DEV_MODE', 'true'),
        },
        result='success',
    )

    from orchestrator import build_orchestrator
    orch = build_orchestrator(str(vault_path))
    orch.start()


if __name__ == '__main__':
    main()
