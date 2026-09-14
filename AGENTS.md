# giulioni.com agent notes

Static personal site. Local checkout: /Users/nickgiulioni/dev/giulioni-com

## Software factory (fleet standard)

Process lives in `AGENTS.md`. Parallel agents stay safe by isolating work, then Build → Prove → Ship. Autopilot means merge-ready, not merge. Nick does not review diffs — agents are the code experts; ask him plain-language product/judgment questions only. Human merges only after Nick’s named yes.

Aligned with Feature craft gate, OpenPStack/pstack / poteto-mode, Mac Studio CLI-first (cloud only if Mac down, model `grok-4.6`), and existing Codex/Sol/Fable review gates. Do not invent a second merge authority.

### 1. Isolate
- Every new feature, fix, or substantial task starts in a **fresh git worktree** branched from `origin/main` (or a base SHA Nick/the plan names) **before any code**.
- Never build on `main`. Never check out the same branch in two worktrees.
- One worktree + one branch per task per agent.
- Never reuse or modify another agent’s worktree, branch, or uncommitted work.
- Scope-check open PRs and recently changed files before starting (avoid file collisions).
- Never force-push to `main` / shared protected branches. `--force-with-lease` only on **your own** unpublished branch when rewriting is required.
- Lockfile conflicts: regenerate the lockfile; do not hand-merge.

**Layout**
- Primary checkout stays on the long-lived base.
- Sibling folder: `<repo-name>-worktrees/` next to the primary checkout.
- One directory per task: `<slug>-YYYYMMDD`.

```sh
git fetch origin
git worktree add -b <feature-branch> ../<repo-name>-worktrees/<slug>-YYYYMMDD origin/main
```

**Cleanup** (after merge or abandon):
```sh
git worktree remove ../<repo-name>-worktrees/<slug>-YYYYMMDD
git worktree prune
```

This file travels with the checkout. Short task overrides belong beside the plan (`PLAN.md`, prompt files), not a divergent permanent root `AGENTS.md`, unless Nick asks for a lasting rule.

### 2. Build
- Use poteto-mode (pstack / OpenPStack) for coding work on Mac Studio CLIs.
- Prefer structure and service-layer discipline over drive-by UI hacks.
- User-facing product work must pass the **Feature craft gate** before calling a slice done.
- Keep changes scoped to the named task. Preserve unrelated WIP elsewhere.
- Spending ladder for CLI work: Qwen 3.8 → GLM 5.3 → MiniMax → Grok 4.6 → Codex Primary → Claude → Codex Reserve (protected). Escalate the uncertain slice, then push execution back down.

### 3. Prove
Before claiming ready, attach **before/after evidence** — not “looks good”:
- Tests that failed then passed (or new tests for the behavior), and/or
- Logs / command receipts with exit codes, and/or
- Screenshots or measurable UI deltas for visual changes, and/or
- Schema/migration/db suite receipts when those surfaces move.

Record what was **not** run. Missing evidence is a blocker, not a footnote.

### 4. Ship
- Open a PR with the proof attached (body or linked receipts).
- Run the repo’s independent review loop to a clear bar (Codex PASS / Sol / Fable-or-Opus per that repo’s AGENTS.md). Map any external “score 5/5” idea onto **those existing gates** — do not add a second merge authority.
- Fix → retest → re-review until no blocking findings remain or Nick accepts a named deferral.
- Hand back: worktree path, branch, commit SHA, PR URL, checks run, leftover gaps.

### 5. Human merges only
- Do not merge or force-push shared branches without Nick’s **named yes** on the ship/wait decision.
- Nick reviews plain-language questions only — never diffs, files, or PR code review homework.
