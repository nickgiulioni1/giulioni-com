# giulioni.com agent notes

Static personal site. Local checkout: /Users/nickgiulioni/dev/giulioni-com

## Git worktrees (fleet standard)

Use a dedicated git worktree for substantial or parallel CLI/agent work. Do not pile unrelated tasks into a dirty primary checkout.

Source pattern: Property Lifecycle (`Developer/property-lifecycle-worktrees/…`) plus Codex AGENTS.md discovery (the worktree checkout carries this file). YouTube `_LCeJZFIsd4` asked for worktrees to be spelled out in AGENTS.md so agents stop inventing layouts.

### Layout
- Keep the primary checkout on the long-lived base (`main` or the named integration branch).
- Sibling folder next to the primary checkout: `<repo-name>-worktrees/`
  - Example: `…/Developer/property-lifecycle` → `…/Developer/property-lifecycle-worktrees/`
  - Example: `…/dev/Best Notes` → `…/dev/Best Notes-worktrees/` (or a short slug sibling if spaces are painful — pick one and stick to it in that repo)
- One directory per task: `<slug>-YYYYMMDD` (example: `accel-preseller-impl-20260912`)

### Create
```sh
git fetch origin
git worktree add -b <feature-branch> ../<repo-name>-worktrees/<slug>-YYYYMMDD origin/main
```
Use a pinned base SHA when Nick or the plan names one. Never reuse another task’s dirty branch as the base unless Nick names that exact base.

### When required
- Substantial implement / fix / review-with-edits
- Parallel Codex, Grok, OpenCode, or Claude sessions on the same repo
- Primary checkout is dirty or owned by another in-flight task

### Rules
1. One branch per worktree. Git will refuse the same branch in two places — do not force it.
2. Preserve unrelated work. Do not reset, clean, or merge foreign WIP into the task worktree.
3. Do not commit secrets, API keys, or noisy CLI logs (`logs/*.jsonl`) unless the repo already tracks that path.
4. Hand back: worktree path, branch, commit SHA, checks run, leftover gaps.
5. Cleanup after merge or abandon:
   ```sh
   git worktree remove ../<repo-name>-worktrees/<slug>-YYYYMMDD>
   git worktree prune
   ```
6. Autopilot means merge-ready, not merge. No merge or force-push to shared branches without Nick’s named yes.

### AGENTS.md in worktrees
This file travels with the checkout. Do not invent a second permanent worktree layout. Short task overrides belong beside the plan (`PLAN.md`, prompt files), not a divergent root `AGENTS.md`, unless Nick asks for a lasting rule.
