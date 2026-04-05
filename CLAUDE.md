# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Personal AI Employee** — a local-first, agent-driven autonomous assistant built for the Panaversity Hackathon 0. The system combines an **Obsidian vault** (GUI + long-term memory) with **Claude Code** (reasoning engine) and **Python watcher scripts** (perception layer) to proactively manage personal and business affairs 24/7.

- **Owner:** Mohsin
- **Timezone:** PKT (UTC+5)
- **Vault path:** `/mnt/c/Users/Mohsin/Desktop/AI_Employee_Vault`
- **Python project:** `ai_employee/` (inside the vault)
- **Target tier:** Bronze (minimum viable deliverable)

## Architecture: Perception → Reasoning → Action

```
External Sources (Gmail, WhatsApp, Files, Bank APIs)
        │
        ▼
  PERCEPTION LAYER — Python Watcher scripts (ai_employee/)
  Lightweight sentinel scripts that monitor inputs and write .md files
        │
        ▼
  OBSIDIAN VAULT (local markdown)
  /Needs_Action  /Plans  /Done  /Logs  /Pending_Approval  /Approved  /Rejected
  Dashboard.md  Company_Handbook.md  Business_Goals.md
        │
        ▼
  REASONING LAYER — Claude Code
  Read → Think → Plan → Write → Request Approval
        │
        ▼
  ACTION LAYER — MCP Servers (email, browser, calendar)
  + Human-in-the-Loop approval via /Pending_Approval → /Approved file moves
```

### Key Components

- **The Brain:** Claude Code — reasoning engine. Reads vault, creates plans, writes reports, requests approvals.
- **The Memory/GUI:** Obsidian vault — all state lives in local markdown files.
- **The Senses (Watchers):** Python scripts in `ai_employee/` that monitor Gmail, WhatsApp, filesystem and write `.md` files into `/Needs_Action`.
- **The Hands (MCP):** Model Context Protocol servers handle external actions (send email, click buttons, etc.).
- **Ralph Wiggum Loop:** A Stop hook pattern that keeps Claude iterating until a multi-step task is complete (Gold tier).

## Vault Folder Structure

```
AI_Employee_Vault/
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Items watchers have flagged for Claude to process
├── Plans/              # Claude-generated plan files with checkboxes
├── Pending_Approval/   # Sensitive actions awaiting human review
├── Approved/           # Human-approved actions ready for execution
├── Rejected/           # Human-rejected actions
├── Done/               # Completed items (archive)
├── Logs/               # Audit logs (JSON, one file per day: YYYY-MM-DD.json)
├── Dashboard.md        # Real-time status: bank balance, pending messages, projects
├── Company_Handbook.md # Rules of engagement (business rules, approval thresholds)
├── Business_Goals.md   # Quarterly objectives, KPIs, subscription audit rules
└── ai_employee/        # Python project (watchers + orchestrator)
```

## Business Rules (from Company_Handbook.md)

These are hard constraints — never violate them:

- All actions must be logged in `/Logs`
- Financial actions over $100 require human approval
- Draft communications go to `/Pending_Approval` — never send autonomously
- Never make payments, post to social media, or share credentials without explicit approval
- Reply to important emails within 24 hours; always CC owner on client emails
- Never delete emails — archive them
- WhatsApp: only respond to messages containing keywords: urgent, invoice, payment, help, asap
- WhatsApp drafts go to `/Pending_Approval` — do not send directly
- Log all transactions in `/Logs`; flag late payment fees immediately
- Generate weekly finance summary every Monday

## Permission Boundaries

| Action Category | Auto-Approve | Always Require Approval |
|----------------|-------------|------------------------|
| Email replies | To known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

## Human-in-the-Loop (HITL) Pattern

For sensitive actions, Claude writes an approval request `.md` file in `/Pending_Approval/` with YAML frontmatter (type, action, amount, recipient, status, expiry). The human reviews and moves the file to `/Approved` to proceed or `/Rejected` to deny. The orchestrator watches `/Approved` and triggers the actual MCP action.

## Watcher Pattern (ai_employee/)

All watchers extend `BaseWatcher` (in `base_watcher.py`):

```python
class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval

    @abstractmethod
    def check_for_updates(self) -> list: ...

    @abstractmethod
    def create_action_file(self, item) -> Path: ...

    def run(self):  # loops forever with sleep(check_interval)
```

Watcher types to implement:
- **GmailWatcher** — polls Gmail API for unread important messages (check_interval=120s)
- **WhatsAppWatcher** — Playwright-based, monitors WhatsApp Web for keyword messages (check_interval=30s)
- **FilesystemWatcher** — uses `watchdog` library to detect file drops, copies to `/Needs_Action`

Action files created by watchers use YAML frontmatter with fields: type, from, subject, received, priority, status.

## Development Commands

```bash
# All commands run from ai_employee/ directory
cd ai_employee

# Setup (requires uv and Python 3.13)
uv sync

# Run main entry point
uv run python main.py

# Run a specific watcher
uv run python gmail_watcher.py
uv run python filesystem_watcher.py

# Add a dependency
uv add <package>
```

## Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Knowledge Base | Obsidian (local markdown) | GUI + long-term memory |
| Logic Engine | Claude Code | Reasoning, planning, writing |
| Package Manager | uv (not pip) | Python dependency management |
| Watchers | Python 3.13 + watchdog | Perception layer |
| External Actions | MCP Servers (Node.js/Python) | Email, browser, calendar |
| Browser Automation | Playwright | WhatsApp, payment portals |
| Process Management | PM2 or supervisord | Keep watchers alive |
| Orchestration | orchestrator.py (master process) | Scheduling + folder watching |

## Security Rules

- **Never** store credentials in vault markdown or commit `.env` files
- Use environment variables or OS credential managers for secrets
- All action scripts must support a `--dry-run` flag
- Implement `DEV_MODE` flag to prevent real external actions during development
- Rate limit: max 10 emails/hour, max 3 payments/hour
- Audit log every action in JSON format to `/Logs/YYYY-MM-DD.json`
- Rotate credentials monthly

## Bronze Tier Deliverables (Current Target)

1. Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
2. One working Watcher script (Gmail OR filesystem monitoring)
3. Claude Code successfully reading from and writing to the vault
4. Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
5. All AI functionality implemented as Agent Skills

## Agent Skills

All AI functionality should be implemented as [Claude Code Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview). This means packaging capabilities as reusable skill definitions rather than one-off scripts.

## Error Handling

- Transient errors (network, rate limit): exponential backoff retry
- Auth errors (expired token): alert human, pause operations
- Logic errors (misinterpretation): route to human review queue
- Never auto-retry payment actions — always require fresh approval
- If Claude Code is unavailable, watchers continue collecting; queue grows for later processing

## Key Conventions

- Lockfile is `uv.lock` — always commit it
- Vault files are markdown with YAML frontmatter
- Log format is JSON with fields: timestamp, action_type, actor, target, parameters, approval_status, approved_by, result
- Retain logs minimum 90 days
- File naming in `/Needs_Action`: `{TYPE}_{identifier}.md` (e.g., `EMAIL_abc123.md`, `WHATSAPP_client_a_2026-01-07.md`, `FILE_document.md`)
- Approval files in `/Pending_Approval`: `{ACTION}_{description}_{date}.md` (e.g., `PAYMENT_Client_A_2026-01-07.md`)
