import os
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from logger import log_action

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FilesystemWatcher')

DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
VAULT_PATH = os.getenv('VAULT_PATH', '/mnt/c/Users/Mohsin/Desktop/AI_Employee_Vault')


class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'

    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        logger.info(f'New file detected: {source.name}')

        if DRY_RUN:
            logger.info(f'[DRY RUN] Would copy {source.name} to Needs_Action')
            self._log_action(source, 'dry_run')
            return

        dest = self.needs_action / f'FILE_{source.name}'
        shutil.copy2(source, dest)
        self._create_metadata(source, dest)
        self._log_action(source, 'success')
        logger.info(f'Copied {source.name} -> {dest.name}')

    def _create_metadata(self, source: Path, dest: Path):
        meta_path = dest.with_suffix('.md')
        now = datetime.now(timezone.utc).isoformat()
        meta_path.write_text(f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
received: {now}
priority: normal
status: pending
---

New file dropped for processing.
''')

    def _log_action(self, source: Path, result: str):
        log_action(
            vault_path=self.vault_path,
            action_type='file_drop_detected',
            actor='filesystem_watcher',
            target=source.name,
            parameters={
                'source_path': str(source),
                'size': source.stat().st_size if source.exists() else 0,
            },
            result=result,
        )


def main():
    watch_dir = Path(VAULT_PATH) / 'Inbox'
    watch_dir.mkdir(parents=True, exist_ok=True)

    handler = DropFolderHandler(VAULT_PATH)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)

    mode = 'DRY RUN' if DRY_RUN else 'LIVE'
    logger.info(f'Filesystem Watcher starting in {mode} mode')
    logger.info(f'Watching: {watch_dir}')
    logger.info(f'Needs_Action: {handler.needs_action}')

    observer.start()
    try:
        while observer.is_alive():
            observer.join(timeout=1)
    except KeyboardInterrupt:
        logger.info('Shutting down...')
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
