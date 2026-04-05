"""Shared audit logging utility for AI Employee watchers."""

import json
from datetime import datetime, timezone
from pathlib import Path


def log_action(
    vault_path: Path,
    action_type: str,
    actor: str,
    target: str,
    parameters: dict,
    result: str,
    approval_status: str = "auto",
    approved_by: str = "system",
) -> None:
    """Append a JSON log entry to /Logs/YYYY-MM-DD.json.

    Args:
        vault_path: Root path of the Obsidian vault.
        action_type: Type of action (e.g. 'file_drop_detected', 'email_fetched').
        actor: Who performed the action (e.g. 'filesystem_watcher', 'gmail_watcher').
        target: What was acted upon (e.g. filename, email subject).
        parameters: Additional context as a dict.
        result: Outcome string (e.g. 'success', 'dry_run', 'error').
        approval_status: 'auto', 'pending', or 'approved'.
        approved_by: 'system', 'human', or 'pending_human'.
    """
    logs_dir = Path(vault_path) / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = logs_dir / f"{today}.json"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_type": action_type,
        "actor": actor,
        "target": target,
        "parameters": parameters,
        "approval_status": approval_status,
        "approved_by": approved_by,
        "result": result,
    }

    entries = []
    if log_file.exists():
        try:
            entries = json.loads(log_file.read_text())
        except (json.JSONDecodeError, ValueError):
            entries = []
    entries.append(entry)
    log_file.write_text(json.dumps(entries, indent=2))
