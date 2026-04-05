---
name: review-vault
description: Perform a read-only audit of the vault. Check folder contents, validate file frontmatter, review Business_Goals.md progress, and report issues.
---

# Review Vault

Perform a comprehensive read-only audit of the entire vault and report findings.

## Steps

1. **Check vault structure** — verify all required folders exist:
   - `Inbox/`, `Needs_Action/`, `Plans/`, `Pending_Approval/`, `Approved/`, `Rejected/`, `Done/`, `Logs/`

2. **Audit each folder**:
   - Count files in each folder
   - For folders with `.md` files, read YAML frontmatter and validate required fields
   - Flag any files with missing or malformed frontmatter

3. **Review key documents**:
   - `Dashboard.md` — is it up to date?
   - `Company_Handbook.md` — does it exist and have complete rules?
   - `Business_Goals.md` — does it exist? Are there active objectives?

4. **Check logs** in `/Logs/`:
   - Read today's log file if it exists
   - Count total log entries for the past 7 days
   - Flag any error entries

5. **Check for stale items**:
   - Items in `Needs_Action/` older than 24 hours (should have been processed)
   - Items in `Pending_Approval/` past their expiry date
   - Plans in `Plans/` with status "active" but no recent activity

6. **Report findings** in a clear summary:
   ```
   VAULT AUDIT REPORT — {date}
   ================================
   Structure:    {OK / issues found}
   Documents:    {status of key .md files}
   Folders:      {item counts per folder}
   Logs:         {entries today / past 7 days}
   Stale Items:  {count and details}
   Issues Found: {list or "None"}
   ```

## Rules
- This is READ-ONLY — do not modify any files
- Report issues but do not fix them
- Suggest corrective actions for any problems found
