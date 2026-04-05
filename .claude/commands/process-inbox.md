Process all pending items in the `/Needs_Action` folder. You are the AI Employee's reasoning engine.

## Steps

1. **Read Company_Handbook.md** at the vault root to load business rules and constraints.
2. **List all `.md` files** in `/Needs_Action` folder.
3. **For each file**, read its YAML frontmatter to determine the type (`email`, `file_drop`, `whatsapp`, etc.).
4. **Apply rules** from Company_Handbook.md based on the item type:
   - **Email items** (`type: email`): Check priority, draft a reply if needed, route draft to `/Pending_Approval`
   - **File drops** (`type: file_drop`): Assess the file, create a processing plan in `/Plans`
   - **WhatsApp items** (`type: whatsapp`): Check for keywords (urgent, invoice, payment, help, asap), draft response to `/Pending_Approval`
   - **Other items**: Create a plan in `/Plans` with suggested next steps
5. **Create a plan file** in `/Plans` for each processed item:
   - Filename: `PLAN_{type}_{identifier}_{date}.md`
   - Include YAML frontmatter: type, created, status, priority, source_file
   - Include a checklist of action steps
6. **For sensitive actions** (payments > $100, emails to new contacts, any autonomous sends):
   - Create an approval request in `/Pending_Approval` instead of acting directly
   - Include: action type, recipient, amount (if financial), reason, expiry (24h from now)
7. **Log each processed item** to `/Logs/YYYY-MM-DD.json` with the standard format:
   ```json
   {
     "timestamp": "ISO-8601",
     "action_type": "inbox_processed",
     "actor": "claude_code",
     "target": "filename",
     "parameters": {"type": "...", "action_taken": "..."},
     "approval_status": "auto|pending",
     "approved_by": "system|pending_human",
     "result": "success"
   }
   ```
8. **Move processed files** from `/Needs_Action` to `/Done` after creating the plan.
9. **Report summary** to the user: how many items processed, what plans were created, what needs approval.

## Important Rules
- NEVER send emails or messages autonomously — always draft to `/Pending_Approval`
- NEVER make payments — create approval request in `/Pending_Approval`
- ALWAYS log every action to `/Logs`
- Read `Company_Handbook.md` FIRST before processing any item
