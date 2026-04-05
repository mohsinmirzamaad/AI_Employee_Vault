Regenerate `Dashboard.md` at the vault root with live status from the vault.

## Steps

1. **Count files** in each vault folder:
   - `Inbox/` — raw incoming items
   - `Needs_Action/` — items awaiting processing
   - `Plans/` — active plans
   - `Pending_Approval/` — items awaiting human review
   - `Approved/` — approved items ready for execution
   - `Rejected/` — rejected items
   - `Done/` — completed items

2. **Read recent log entries** from `/Logs/` (today's file and yesterday's if available). Summarize the last 5 actions.

3. **List items needing attention**:
   - Files in `Needs_Action/` (show type and subject from frontmatter)
   - Files in `Pending_Approval/` (show action type and summary)

4. **Check Business_Goals.md** if it exists — show current quarter objectives and progress.

5. **Write Dashboard.md** with this structure:
   ```markdown
   ---
   type: dashboard
   last_updated: YYYY-MM-DDTHH:MM:SS+05:00
   ---

   # AI Employee Dashboard

   ## System Status
   - **Mode:** DRY_RUN / LIVE (check .env if accessible, otherwise note unknown)
   - **Last Updated:** {current date and time in PKT}

   ## Folder Summary
   | Folder | Items |
   |--------|-------|
   | Inbox | {count} |
   | Needs Action | {count} |
   | Plans | {count} |
   | Pending Approval | {count} |
   | Done | {count} |

   ## Needs Attention
   {list items from Needs_Action with type and subject, or "Nothing pending."}

   ## Awaiting Approval
   {list items from Pending_Approval, or "Nothing awaiting approval."}

   ## Recent Activity
   {last 5 log entries summarized, or "No recent activity."}

   ## Business Goals
   {summary from Business_Goals.md or "Not configured."}
   ```

6. **Log the dashboard update** to `/Logs/YYYY-MM-DD.json`.

## Notes
- Use PKT timezone (UTC+5) for all timestamps
- Keep the dashboard concise — it should be scannable in under 30 seconds
