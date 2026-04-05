---
name: create-plan
description: Create a structured plan file in the Plans folder for a given task or objective with YAML frontmatter and step-by-step checkboxes.
---

# Create Plan

Generate a structured plan file in `/Plans` for a task the user describes.

## Steps

1. **Ask or infer** the task objective from the user's input.

2. **Create a plan file** at `/Plans/PLAN_{short_description}_{date}.md` with:
   ```markdown
   ---
   type: plan
   created: {ISO-8601 timestamp in PKT}
   status: active
   priority: {high|medium|low}
   objective: "{brief one-line objective}"
   ---

   # Plan: {Objective Title}

   ## Objective
   {1-2 sentence description of what needs to be accomplished}

   ## Steps
   - [ ] Step 1: {description}
   - [ ] Step 2: {description}
   - [ ] Step 3: {description}
   ...

   ## Approval Required
   {List any steps that need human approval, or "None — all steps are auto-approvable."}

   ## Success Criteria
   - {How to verify the plan is complete}

   ## Notes
   - {Any relevant context, constraints, or dependencies}
   ```

3. **Log the plan creation** to `/Logs/YYYY-MM-DD.json`.

4. **Report** the plan filename and summary to the user.

## Guidelines
- Keep plans actionable — each step should be a concrete task
- Flag any step that requires human approval (payments, external communication)
- Plans for financial actions should always include an approval step
- Use PKT timezone (UTC+5) for all timestamps
