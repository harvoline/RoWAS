# Coding / Git Workflow

## Branching

`main` must always remain stable and deployable. No feature work is ever
committed directly to `main`.

```
main
 ├── feature/<short-description>
 ├── fix/<short-description>
 └── chore/<short-description>       (tooling/docs-only changes)
```

Examples: `feature/robot-allocation-core`, `fix/allocation-tie-break`,
`chore/ci-setup`.

## Commits

- Each commit should represent one coherent, logically understandable
  change. Do not bundle unrelated changes.
- Commit messages must explain *why*, not just *what* (the diff already
  shows *what*).
- Avoid giant commits. A scaffolding change, a business feature, and a
  documentation update are three commits, not one.

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

- Required before merging any feature/fix branch into `main`.
- The project owner reviews and approves.
- **Open item:** no remote repository/hosting platform is currently
  configured (`git remote -v` is empty), so the concrete PR mechanism
  (GitHub PR vs. DevSwarm's own merge workflow) is undecided. This must be
  resolved before or at the first real PR.

## Environment-Specific Note

This workspace runs under DevSwarm. Native Windows shells cannot execute
git commands here because the `.git` worktree pointer resolves to a WSL-only
path. All git commands (`status`, `add`, `commit`, `branch`, etc.) must be
run from WSL against the same directory via its `/mnt/c/...` path. See
`CLAUDE.md` "Important Constraints" for the full explanation.
