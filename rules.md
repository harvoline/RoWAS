# Project Rules (Non-Negotiable)

These rules apply to every contributor — human or AI — working on this
repository. They do not get silently overridden by convenience.

## Safety

- Never execute destructive commands without explicit approval (deleting
  files, branches, databases, volumes, or infrastructure).
- Never perform irreversible operations without approval (force-push,
  history rewrite, `git reset --hard`, discarding uncommitted work).
- Never overwrite important user work without approval.
- If a command may be destructive and there is any uncertainty: **stop and
  ask for approval** before running it.
- **Do not "fix" git internals (`.git` files, worktree pointers, etc.) you
  don't fully understand just because a command failed unexpectedly.**
  Some managed/sandboxed environments deliberately route git through a
  different path or shell — that's an environment quirk to document in a
  local `user-setup.md` (see `documentation-workflow.md`), not something to
  repair by editing git's internal files. If a git command fails in a way
  that looks like infrastructure rather than a real repo problem, diagnose
  first (e.g. check whether it works from a different shell) before
  touching anything inside `.git`.

## Engineering

- Follow the established architecture (see `CLAUDE.md`) — do not silently
  introduce a different structure without discussing the change first.
- Follow existing project conventions.
- Prefer simple solutions over unnecessary complexity.
- Avoid premature abstraction — no framework, layer, or interface until a
  second real use case demands it.
- Avoid unnecessary dependencies. Every dependency added must have a
  documented reason (see `solutions.md`).
- Keep responsibilities separated: CLI/IO concerns, validation, and business
  logic must not be mixed together.
- Validate all external/user input explicitly.
- Handle errors explicitly — do not swallow exceptions or fail silently.
- Do not introduce technical debt without documenting it in `README.md`
  ("Technical Debt" section) and, if significant, `solutions.md`.

## Changes

Before making a significant architectural change:

1. Explain the problem.
2. Explain the proposed solution.
3. Explain alternatives considered.
4. Explain trade-offs.
5. Get explicit approval if the decision materially affects architecture.

Do not silently change an established architectural decision recorded in
`CLAUDE.md`.

## CI/CD Checkpoint

**Resolved 2026-09-05, at PR #1 (the foundation PR).** The project owner
was presented with the platform (GitHub, `harvoline/RoWAS`), an event-driven
GitHub Actions option, and the previously-discussed 3-hour scheduled build,
and chose to **defer CI/CD entirely** rather than adopt either. This is a
considered decision, not an unresolved gap — see `solutions.md` for the full
reasoning. Do not add CI/CD configuration without raising it again first;
treat any future addition as a new decision to be proposed, not a
resumption of "the open item."

## Pull Request Review

Every pull request requires review before merge — reviewers use GitHub's
Approve / Request changes / Comment actions, and all review comments must be
addressed (either by a follow-up commit or an explicit reply explaining why
not) before merging. This is a **process rule, not currently a technical
gate**: RoWAS is a private repository on GitHub's Free plan, which blocks
both classic branch protection and rulesets (confirmed via the API:
"Upgrade to GitHub Pro or make this repository public"), and there is
currently only one collaborator. Nothing stops a self-merge today except
discipline.

**Do not treat the absence of a technical gate as permission to skip
review.** If/when a second collaborator joins, or the plan is upgraded, or
the repo goes public, revisit this and add real branch protection
(required approvals, no direct pushes to `main`) — see `CLAUDE.md` Known
Decisions for status.

## Multi-Agent Workflow

See `orchestrator-workflow.md` for the full delegation model. The "Safety"
and "Changes" rules above apply identically regardless of whether a human
or a specialist subagent produced a recommendation — a specialist agent's
output is a recommendation to the Orchestrator, never an authorization to
act. Two additions specific to multi-agent delegation:

- Introducing a new orchestration layer (sub-orchestrators) requires the
  documented justification in `orchestrator-workflow.md` to be updated and
  presented first — not silently added because the tooling allows it.
- Changing the specialist roster (`.claude/agents/*.md`) is a process
  change and should be surfaced to the project owner, though it does not
  require the same stop-and-ask as the destructive/architectural items
  above.

## Business Requirements

Levels 1-4 are implemented from owner requirements. New allocation levels or
changes to business rules still require explicit owner requirements; do not
invent them from implementation convenience. Current shared rules live in
`robots.md`, with per-level rules in `features/`.
