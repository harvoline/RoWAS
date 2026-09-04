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
| Git/process workflow changes | `coding-workflow.md` |
| Testing strategy changes | `testing-workflow.md` |
| New infrastructure / tooling | `CLAUDE.md`, `README.md` |
| Technical debt introduced or removed | `README.md` "Technical Debt" section |
| Significant technical decision made | `solutions.md` |
| Meaningful AI tool usage | `tools.md` |

## What Not to Document

Do not document implementation details that will go stale quickly (e.g. "line
42 does X") unless understanding that specific detail is important to
maintaining the system. Prefer documenting **why** something exists over
**what** the code visibly does — the code already says what it does.

## Ownership

Whoever makes the change (human or AI) updates the documentation in the same
commit/PR — not as a follow-up "docs" task.
