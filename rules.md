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
  logic must not be mixed together once business logic exists.
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

## Business Logic Freeze

Robot allocation business functionality must not be implemented until the
project owner explicitly provides the requirement. This rule was set during
foundation setup and remains in force until superseded by a later
instruction — check `CLAUDE.md` "Known Decisions" for the current status
before assuming it still applies.
