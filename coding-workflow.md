# Coding / Git Workflow

## Branching

`main` must always remain stable and deployable. No feature work is ever
committed directly to `main`.

```
main
 ├── feature/<short-description>
 ├── fix/<short-description>
 ├── chore/<short-description>       (tooling/docs-only changes)
 └── TR<nn>_<SHORT_NAME>             (accepted EverBot exercise convention)
```

Examples: `feature/robot-allocation-core`, `fix/allocation-tie-break`,
`chore/ci-setup`, `TR02_LEVEL_1`, `TR03_LEVEL_2`.

The `TR<nn>_…` form is an **accepted project convention** for sequenced
exercise/level work (same rules as `feature/`: branch from `main`, one
coherent change, merge via PR). Prefer `feature/` / `fix/` / `chore/` for
non-exercise work; use `TR…` when continuing the numbered EverBot level track.

## Commits

- Each commit should represent one coherent, logically understandable
  change. Do not bundle unrelated changes.
- Commit messages must explain *why*, not just *what* (the diff already
  shows *what*).
- Avoid giant commits. Include directly related documentation with the code or
  decision it describes; separate unrelated scaffolding or documentation work.

## The Full Cycle

```
Requirement
    -> Analysis
    -> Plan
    -> Create feature branch
    -> Write failing test (RED)
    -> Implement (GREEN)
    -> Run tests / lint / type-check
    -> Refactor
    -> Commit
    -> Open pull request
    -> Review
    -> Approval
    -> Merge to main
    -> CI/CD (once decided — see rules.md CI/CD Checkpoint)
```

## Pull Requests

Hosted on GitHub: [harvoline/RoWAS](https://github.com/harvoline/RoWAS).
Required before merging any feature/fix branch into `main`.

**Opening a PR:**

- Use the PR template (`.github/pull_request_template.md`) — fill in the
  summary, link the requirement/issue it addresses, and complete the
  verification checklist (tests/lint/type-check actually run, docs updated).
- `CODEOWNERS` currently routes every PR to the project owner for review.

**Reviewing a PR:**

- Use GitHub's native review actions on the "Files changed" tab:
  - **Comment** — feedback that doesn't block merge on its own.
  - **Request changes** — blocks merge (by convention, see below) until
    resolved.
  - **Approve** — signals the PR is ready to merge as-is.
- Leave inline comments on specific lines where possible; use the overall
  review summary for cross-cutting feedback.

**Responding to review feedback:**

- Address each comment with a new commit (don't rewrite/force-push history
  that's already been reviewed — that hides what changed in response to
  feedback). Reply to the comment thread explaining what changed, or why
  not, if you disagree.
- Re-request review once feedback is addressed.
- Merge only once outstanding "Request changes" reviews are resolved and at
  least one approval exists.

**Enforcement status:** this is currently a **convention, not a technical
gate** — RoWAS is a private repo on GitHub's Free plan, which blocks branch
protection/rulesets, and there is only one collaborator today. See
`rules.md` "Pull Request Review" for the full reasoning and the conditions
under which this gets revisited.

## Environment-Specific Notes

This project must run identically regardless of OS or host environment —
no environment-specific instructions belong in the tracked docs. If your
machine needs a different invocation for a standard command (git, python,
etc.), keep that in your own local, gitignored `user-setup.md` at the repo
root rather than here. See `documentation-workflow.md`.
