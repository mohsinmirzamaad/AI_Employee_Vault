"""Orchestrator — master process that manages all watchers.

Starts configured watchers in daemon threads, monitors health,
and handles clean shutdown.

Usage:
  Called from main.py, or directly:
  uv run python orchestrator.py
"""

import os
import signal
import sys
import logging
import threading
from pathlib import Path

from logger import log_action

logger = logging.getLogger('Orchestrator')

VAULT_PATH = os.getenv('VAULT_PATH', '/mnt/c/Users/Mohsin/Desktop/AI_Employee_Vault')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
DEV_MODE = os.getenv('DEV_MODE', 'true').lower() == 'true'


class Orchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.watchers = []
        self.threads: list[threading.Thread] = []
        self.running = True

    def register_watcher(self, watcher, name: str):
        """Register a watcher instance to be managed."""
        self.watchers.append((name, watcher))
        logger.info(f'Registered watcher: {name}')

    def start(self):
        """Start all registered watchers in daemon threads."""
        mode = 'DRY RUN' if DRY_RUN else 'LIVE'
        dev = ' (DEV MODE)' if DEV_MODE else ''
        logger.info(f'Orchestrator starting in {mode}{dev} mode')
        logger.info(f'Vault: {self.vault_path}')
        logger.info(f'Watchers: {len(self.watchers)}')

        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        for name, watcher in self.watchers:
            t = threading.Thread(target=self._run_watcher, args=(name, watcher), daemon=True)
            t.start()
            self.threads.append(t)
            logger.info(f'Started watcher thread: {name}')

        log_action(
            vault_path=self.vault_path,
            action_type='orchestrator_started',
            actor='orchestrator',
            target='system',
            parameters={
                'watchers': [name for name, _ in self.watchers],
                'dry_run': DRY_RUN,
                'dev_mode': DEV_MODE,
            },
            result='success',
        )

        # Block main thread until shutdown
        try:
            while self.running:
                for t in self.threads:
                    t.join(timeout=1.0)
        except KeyboardInterrupt:
            self._shutdown(None, None)

    def _run_watcher(self, name: str, watcher):
        """Run a watcher with error recovery."""
        try:
            watcher.run()
        except Exception as e:
            logger.error(f'Watcher {name} crashed: {e}')
            log_action(
                vault_path=self.vault_path,
                action_type='watcher_crashed',
                actor='orchestrator',
                target=name,
                parameters={'error': str(e)},
                result='error',
            )

    def _shutdown(self, signum, frame):
        """Clean shutdown of all watchers."""
        logger.info('Shutting down orchestrator...')
        self.running = False

        log_action(
            vault_path=self.vault_path,
            action_type='orchestrator_stopped',
            actor='orchestrator',
            target='system',
            parameters={},
            result='success',
        )

        sys.exit(0)


def build_orchestrator(vault_path: str) -> Orchestrator:
    """Build an orchestrator with all available watchers registered."""
    orch = Orchestrator(vault_path)

    # Always register filesystem watcher (no external deps)
    from filesystem_watcher import DropFolderHandler
    from watchdog.observers import Observer

    class FilesystemWatcherRunner:
        """Adapter to run the watchdog-based filesystem watcher."""
        def __init__(self, vp: str):
            self.vault_path = vp

        def run(self):
            watch_dir = Path(self.vault_path) / 'Inbox'
            watch_dir.mkdir(parents=True, exist_ok=True)
            handler = DropFolderHandler(self.vault_path)
            observer = Observer()
            observer.schedule(handler, str(watch_dir), recursive=False)
            observer.start()
            logger.info(f'Filesystem watcher watching: {watch_dir}')
            try:
                while True:
                    observer.join(timeout=1)
            except Exception:
                observer.stop()
            observer.join()

    orch.register_watcher(FilesystemWatcherRunner(vault_path), 'filesystem')

    # Conditionally register Gmail watcher
    gmail_creds = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    if Path(gmail_creds).exists() or DEV_MODE:
        from gmail_watcher import GmailWatcher
        orch.register_watcher(GmailWatcher(vault_path), 'gmail')
    else:
        logger.info('Gmail watcher skipped — no credentials.json found')

    return orch


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    orch = build_orchestrator(VAULT_PATH)
    orch.start()


if __name__ == '__main__':
    main()
