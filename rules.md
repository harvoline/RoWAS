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
- **Do not "fix" the `.git` worktree pointer files in this repository.**
  They intentionally point to a Linux path (`/var/www/rows`) managed by
  DevSwarm. This is expected architecture, not corruption — see
  [`CLAUDE.md`](CLAUDE.md) "Important Constraints." Editing them risks
  breaking the workspace's connection to the real git object database.
- **All git operations in this workspace must run through WSL** (see
  `CLAUDE.md`), never through a native Windows shell — native Windows git
  cannot resolve the worktree pointer and will fail or, worse, could be
  worked around in a way that desynchronises the Windows mirror from the
  real repository.

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

## Business Logic Freeze

Robot allocation business functionality must not be implemented until the
project owner explicitly provides the requirement. This rule was set during
foundation setup and remains in force until superseded by a later
instruction — check `CLAUDE.md` "Known Decisions" for the current status
before assuming it still applies.
