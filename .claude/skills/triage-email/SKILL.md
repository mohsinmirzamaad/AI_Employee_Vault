---
name: triage-email
description: Triage an email item from Needs_Action. Analyze priority, draft a reply following Company_Handbook email rules, and route to the correct folder.
---

# Triage Email

Process email items (`EMAIL_*.md` files) from `/Needs_Action` using the email rules in `Company_Handbook.md`.

## Steps

1. **Read Company_Handbook.md** to load email-specific rules:
   - Reply within 24 hours for important emails
   - Always CC owner on client emails
   - Never delete emails — archive them
   - Never send emails without human approval

2. **Find email files** in `/Needs_Action` matching pattern `EMAIL_*.md`.

3. **For each email**, read the YAML frontmatter and body:
   - Determine sender (known contact vs new contact)
   - Assess priority (high/medium/low based on frontmatter and content)
   - Identify required action (reply, forward, archive, escalate)

4. **Draft a reply** if one is needed:
   - Create a draft file in `/Pending_Approval/EMAIL_REPLY_{identifier}_{date}.md`
   - Include YAML frontmatter:
     ```yaml
     ---
     type: approval_request
     action: send_email
     to: {sender_email}
     cc: mohsin@{owner_email}
     subject: "Re: {original_subject}"
     priority: {high|medium|low}
     created: {ISO-8601}
     expires: {24h from now, ISO-8601}
     status: pending
     ---
     ```
   - Write a professional, polite reply body
   - Add instructions: "Move to /Approved to send, or /Rejected to discard"

5. **Create a plan** in `/Plans/PLAN_EMAIL_{identifier}_{date}.md` with:
   - Summary of the email
   - Checklist: [ ] Review draft reply, [ ] Approve or reject, [ ] Archive original

6. **Log the triage action** to `/Logs/YYYY-MM-DD.json`.

7. **Report** what was triaged and what needs approval.

## Rules
- NEVER send emails directly — all replies go to `/Pending_Approval`
- For emails from new/unknown contacts, flag as needing extra review
- For client emails, always include CC to owner in the draft
