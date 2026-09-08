# Documentation Workflow

Documentation is part of development, not an afterthought. A change is not
"done" until the relevant documentation reflects it.

## Standards

Documentation should be:

- Human-readable and accurate.
- Concise where possible, detailed where necessary.
- Consistent with the actual state of the code (stale docs are worse than
  no docs).
- Useful to a developer who has never seen the project before.

## When to Update Documentation

| Trigger | Update |
|---|---|
| Architecture changes | `CLAUDE.md` |
| Business rule changes | `app-workflow.md`, and `CLAUDE.md` domain context if the change is foundational |
| Shared robot or level rules change | `robots.md`, affected `features/level-*.md`, with changelog entries |
| Shared CLI behaviour changes | `app-workflow.md`, `README.md`, `testing-workflow.md`; link shared behaviour from level specs |
| Git/process workflow changes | `coding-workflow.md` |
| Testing strategy changes | `testing-workflow.md` |
| New infrastructure / tooling | `CLAUDE.md`, `README.md` |
| Technical debt introduced or removed | `README.md` "Technical Debt" section |
| Significant technical decision made | `solutions.md` |
| Meaningful AI tool usage | `tools.md` |
| Multi-agent workflow / specialist roster changes | `orchestrator-workflow.md`, `.claude/agents/*.md` |

## What Not to Document

Keep README short: setup, approach, design decisions, assumptions, trade-offs,
verification, and prioritised improvement areas. Link detailed specifications and
decision records instead of duplicating them. Refresh current-state claims across
contributor/agent guides when they drift. Preserve dated historical records; append
a new entry when later evidence changes an earlier assessment.

Do not document implementation details that will go stale quickly (e.g. "line
42 does X") unless understanding that specific detail is important to
maintaining the system. Prefer documenting **why** something exists over
**what** the code visibly does — the code already says what it does.

## Ownership

Whoever makes the change (human or AI) updates the documentation in the same
commit/PR — not as a follow-up "docs" task.

## Machine-Specific Setup Notes Are an Exception

Every file listed above is tracked in git and must apply to any contributor
on any machine — no OS-, shell-, or sandbox-specific instructions belong in
them. If a real environment quirk needs documenting (e.g. a managed dev
environment that changes how a standard command must be invoked), it goes
in a local `user-setup.md` at the repo root instead. That file is
gitignored, per-developer, and exempt from the "update in the same PR" rule
above — it isn't shared project documentation, so there's nothing to keep
in sync across contributors. See `CLAUDE.md` "Important Constraints" and
`rules.md` "Safety" for why this distinction matters (a past instance of
mixing the two caused a machine-specific git workaround to leak into the
shared project context file).
