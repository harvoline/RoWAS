# Solutions Log

Detailed record of significant technical problems and the reasoning behind
their solutions. This file preserves *why*, not just *what*.

---

## 1. Establishing the Engineering Foundation for an Empty Repository

### Problem

The repository contained nothing but an empty initial commit. No language,
framework, structure, or tooling existed. A production-oriented CLI
application needs to be built incrementally on top of a foundation that
supports TDD, disciplined git workflow, and clear documentation — but that
foundation didn't exist yet.

### Context

The project owner's process specification explicitly forbids implementing
business functionality before the foundation is established and approved,
and explicitly forbids assuming a technology stack when it "cannot
reasonably be inferred."

### Requirements

- A working, verified project skeleton (not just files that look right —
  actually installable and runnable).
- Test, lint, and type-check tooling wired up and passing.
- A documentation system covering context, tool usage, technical decisions,
  application workflow, git workflow, testing strategy, rules, and
  documentation process itself.
- No business logic.
- CI/CD explicitly deferred, recorded as an open decision.

### Constraints

- Cannot infer the programming language — this materially affects
  architecture, testing framework, and tooling, so it required asking
  rather than assuming.
- The repository is empty, so there were no existing conventions to
  discover and follow; conventions had to be established from scratch and
  justified.

### Analysis

Considered stacks: TypeScript/Node.js, Python, Java, C#. Each is a
reasonable choice for a rules-heavy terminal application; none could be
confidently inferred from the (empty) repository. Presented as a choice
rather than picking one, per the instruction to ask when a decision
materially affects architecture. **Decision: Python**, made by the project
owner.

Within Python, considered:

- **Flat vs. src-layout package structure.** Src-layout was chosen: it
  prevents a common footgun (tests accidentally importing the local
  directory instead of the installed package), which matters for keeping
  test results trustworthy — directly serves the "correctness" and
  "testability" priorities in the project's stated assessment criteria.
- **Poetry/PDM/hatchling vs. setuptools for packaging.** setuptools was
  chosen: it is bundled with virtually every Python installation and pip,
  needs no extra tool to learn, and the project's own rules explicitly say
  to avoid unnecessary dependencies. Poetry/PDM would add a second
  dependency-resolution tool for no benefit at this stage (no complex
  dependency graph exists yet).
- **Whether to add lint/type-check tooling now versus later.** Added now:
  the project's stated assessment criteria include "code structure and
  maintainability" and "production readiness" from the start, and
  retrofitting `mypy --strict` onto untyped code later is materially more
  expensive than writing typed code from the first line. ruff was chosen
  over separate flake8+black+isort because it is one dependency instead of
  three, with equivalent coverage.

### Delegation

No sub-tasks were delegated to other agents — the foundation work is small
enough, and requires enough continuity of context (the language decision
affects every subsequent file), to do directly.

### Decision

- Language: **Python >= 3.10** (owner decision).
- Layout: **src-layout**, package name `robot_allocation` (later renamed to `everbot` — see entry below).
- Build backend: **setuptools**.
- Dev tooling: **pytest + pytest-cov, ruff, mypy(strict)**.
- CLI entry point exists (`cli.py`) but contains no business logic — only a
  placeholder banner — to respect the explicit "do not implement business
  logic yet" instruction while still proving the scaffolding is real and
  runnable.

### Reasoning

Every tool choice above is justified by a stated project priority
(maintainability, testability, avoiding unnecessary dependencies) rather
than by default/habit. The CLI placeholder was added specifically because a
*silent, untested* scaffold would violate "never claim a test/build
succeeded unless it was actually executed and verified" — there had to be
something real to run and test.

### Implementation Order

1. Write failing test for the CLI entry point (RED).
2. Add `pyproject.toml`, `.gitignore`, package skeleton (`cli.py`,
   `__init__.py`).
3. Implement minimal `cli.py` to pass the test (GREEN).
4. Verify for real: build a virtualenv, install in editable mode, run
   pytest/ruff/mypy, confirm all pass.
5. Write the documentation set, referencing the now-verified decisions.
6. Commit in logically separated commits (scaffolding, then docs).

### Trade-offs

- **Pro:** minimal dependency footprint, standard/boring tooling choices
  that any Python developer will recognise immediately, strict typing from
  day one avoids expensive retrofitting.
- **Con:** `mypy --strict` adds friction for every future contributor —
  every function needs full type annotations. Accepted because the
  project's stated priority order is "correctness -> maintainability ->
  testability -> clarity -> production readiness," and strict typing
  directly serves the first two.
- **Con:** no CI/CD yet means these checks (`pytest`, `ruff`, `mypy`) are
  only enforced if a developer remembers to run them locally. This is a
  known, accepted gap until the CI/CD checkpoint (see `rules.md`) is
  resolved.

### Result

A verified, minimal Python project skeleton: `pyproject.toml` (setuptools,
src-layout, pytest/ruff/mypy config), `src/robot_allocation/{__init__.py,
cli.py}` (since renamed to `src/everbot/`), `tests/test_cli.py`. Confirmed working end-to-end: `pytest` (1
passed), `ruff check .` (all checks passed), `mypy src` (no issues, strict
mode). Full documentation set written alongside it.

### Future Considerations

- The `strict = true` mypy setting may need per-module relaxation if a
  future dependency lacks type stubs — deal with that when it happens
  rather than pre-emptively loosening it now.
- The CLI placeholder in `cli.py` must be replaced (not just extended) once
  real input/output requirements arrive — it is scaffolding, not a
  foundation to build features on top of untouched.
- Package name was later renamed from `robot_allocation` to `everbot` (owner decision; see Level 1 port entry).

---

## 2. Diagnosing the DevSwarm Git/WSL Environment Mismatch

### Problem

Every native (Windows Git Bash) `git` command failed with `fatal: not a
git repository: /var/www/rows/.git/worktrees/initial-setup` — a Linux path
that does not exist on Windows. This blocked the very first step of the
process (inspecting existing git state).

### Context

This repository is managed by DevSwarm (`hivecontrol`), which — per its own
CLI output — expected a `claude-wsl` agent, i.e. it assumed git operations
would happen inside WSL, not a native Windows shell.

### Requirements

Confirm whether this indicated actual repository corruption (requiring
recovery) or an environment/tooling mismatch (requiring a different
invocation method).

### Constraints

Must not attempt destructive git recovery operations without being certain
of the root cause first (per safety rules).

### Analysis

1. Compared this repository's `.git` pointer file against four sibling
   DevSwarm repositories on the same machine — all four showed the
   identical pattern (`gitdir: /var/www/<project>/.git/worktrees/<branch>`),
   ruling out one-off corruption.
2. Confirmed a real WSL distribution (`Ubuntu-20.04`) is installed and
   running (`wsl.exe -l -v`).
3. Confirmed the referenced path exists inside WSL and contains real git
   worktree metadata (`HEAD`, `index`, `logs`, `refs`).
4. Confirmed the worktree's `gitdir` file points back to
   `/mnt/c/Users/Afif/.devswarm/repos/2/dfb88366/initial-setup/.git` — the
   same directory, reachable from WSL via its `/mnt/c/...` mount. This is a
   standard, correctly-formed git worktree cross-reference; the only issue
   is that Windows-native git cannot resolve the Linux-side half of it.
5. Verified the fix by running `git status`/`git log` from inside WSL
   against the `/mnt/c/...` path — worked immediately, showed the true
   repository state (one empty "Initial commit," no remote, current branch
   `initial-setup` off `main`).

### Delegation

Not applicable — single diagnostic thread.

### Decision

All git operations in this workspace must be issued via WSL
(`wsl.exe -d Ubuntu-20.04 -- bash -c "cd /mnt/c/... && git ..."`), never via
native Windows git. File edits (non-git) work fine from either side since
it's the same underlying filesystem.

### Reasoning

The repository is not corrupted; it is a correctly functioning git
worktree whose two halves live in different OS environments that only WSL
can bridge. Changing invocation method costs nothing and is fully
reversible; attempting to rewrite the `.git` pointer files would be a
destructive, unnecessary risk to working infrastructure.

### Implementation Order

Diagnose -> confirm via sibling repos -> confirm WSL bridges both paths ->
adopt WSL as the git invocation method -> document in `CLAUDE.md` and
`rules.md` so future sessions don't re-diagnose this from scratch.

### Trade-offs

**Con:** every git command in this project now requires wrapping in a
`wsl.exe` invocation, which is a small amount of friction and an
easy-to-forget detail for a future contributor unfamiliar with DevSwarm.
Mitigated by documenting it prominently in `CLAUDE.md`, `rules.md`, and
`README.md`.

### Result

Git operations work reliably for the remainder of this session and future
sessions, without any change to the repository itself.

### Future Considerations

If this workspace is ever migrated off DevSwarm or the WSL distribution
changes, this constraint should be re-verified and the documentation
updated or removed accordingly.

---

## 3. Configuring the Remote Repository and Resolving the CI/CD Checkpoint

### Problem

The foundation work existed only as local commits. Two things blocked
opening the first pull request: no remote repository was configured, and
CI/CD strategy was explicitly left as an open decision pending this exact
checkpoint (see `rules.md` "CI/CD Checkpoint").

### Context

The project owner supplied a GitHub repository URL
(`https://github.com/harvoline/RoWAS.git`) to use as the remote. This is
also, by the project's own process, the moment CI/CD must be revisited —
"When we are preparing for the first Pull Request, STOP and explicitly ask."

### Requirements

- Confirm the remote is real and usable before pushing anything to it.
- Get explicit approval before pushing/opening a PR — pushing code and
  opening a PR are actions visible to others and affect shared state.
- Present CI/CD alternatives with trade-offs and let the owner decide,
  rather than silently implementing (or silently skipping) anything.

### Constraints

- Must not push destructively or assume push is wanted just because a URL
  was provided — confirmed the specific plan (push `main`, push
  `initial-setup`, open PR) before executing it.

### Analysis

Checked the remote read-only first (`git ls-remote`) before adding it as
`origin`: reachable, zero refs (a genuinely empty repository, not one with
existing history that could conflict). Confirmed `gh` was already
authenticated as the repository owner (`harvoline`), so PR creation would
not require additional credential setup.

For CI/CD, presented three options once the platform (GitHub) was known:

1. GitHub Actions on PR open/update + push to `main` — event-driven,
   fastest feedback, standard for a repo this size.
2. The same, plus the previously-discussed 3-hour scheduled build — the
   schedule adds no value for catching code issues (PR-triggered checks
   already run within seconds of a push), so its only justification would
   be catching drift unrelated to code changes (e.g. dependency rot) —
   speculative at this stage, no dependencies exist yet to drift.
3. Defer CI/CD entirely — no workflow file at all yet.

### Delegation

Not applicable.

### Decision

- **Remote:** `origin` = `https://github.com/harvoline/RoWAS.git`. Pushed
  `main` (stable base) and `initial-setup` (foundation work), opened PR #1
  from `initial-setup` into `main`.
- **CI/CD:** the project owner chose to **defer CI/CD entirely** — option 3.
  No GitHub Actions workflow was added.

### Reasoning

Deferring is reasonable at this stage: there is no business logic yet, the
dependency set is four dev-only packages, and local verification
(`pytest`/`ruff`/`mypy`) is already enforced as part of the definition of
"done" for any change (see `testing-workflow.md`). A CI workflow would
currently just re-run the same three commands the developer already ran
locally, for a project with a single contributor so far — real value
appears once there's enough velocity or enough contributors that "did the
developer actually run the checks" becomes a meaningful question. This
was the owner's call to make, not an inference.

### Implementation Order

1. `git ls-remote` (read-only) to confirm the remote is real and empty.
2. Confirm plan with the owner (push + PR; CI/CD strategy) before acting.
3. `git remote add origin`, push `main`, push `initial-setup`.
4. `gh pr create` — hit a shell-quoting bug where backticks in the PR body
   were evaluated as command substitution by an intermediate shell layer
   (nested `bash -c` invocations across the Windows/WSL boundary), silently
   stripping code-formatted terms from the body. Fixed by writing the body
   to a file and using `gh pr edit --body-file`, sidestepping shell
   quoting entirely. Recorded in `tools.md` as a discovered risk: **avoid
   passing markdown with backticks through nested shell `-c` strings in
   this environment — write to a file first.**
5. Updated `CLAUDE.md`, `README.md`, and `rules.md` to reflect both
   decisions as confirmed, not open.

### Trade-offs

- **Pro:** zero CI maintenance burden while the project has no business
  logic; nothing to get wrong in a workflow file that isn't earning its
  keep yet.
- **Con:** no automated gate stops a broken commit from landing on `main`
  if a future contributor forgets to run checks locally. Accepted
  explicitly by the owner; revisit once that risk becomes real (more
  contributors, or `main` starts carrying real functionality).

### Result

`origin` configured and both branches pushed. PR #1 open at
`https://github.com/harvoline/RoWAS/pull/1`, awaiting owner review. No CI/CD
configuration exists. Both decisions recorded as **Confirmed** in
`CLAUDE.md`'s Known Decisions table.

### Future Considerations

Revisit CI/CD the moment either becomes true: (a) a second contributor
joins, or (b) `main` starts carrying real business logic where a broken
merge would have user-facing consequences. At that point, option 1
(event-driven GitHub Actions) is the standing recommendation.

---

## 4. Making CLAUDE.md Portable and Establishing the PR Review Process

### Problem

Two issues surfaced from the owner's review of PR #1: (1) `CLAUDE.md`
contained a machine-specific detail (the DevSwarm/WSL git redirection) that
would be actively misleading to a contributor on Mac/Linux/plain Windows,
and (2) the project needed an actual team review workflow (comment,
approve, request changes) rather than an implicit assumption that PRs get
merged after being looked at.

### Context

The owner correctly flagged, via an inline PR review comment on
`CLAUDE.md` line 119, that the project cannot control where it will be run,
so environment-specific constraints shouldn't live in a file meant to
describe the *project*. Separately, they asked for the repository to be
set up "like a proper team flow" with commenting and approve/reject
reviews.

### Requirements

- `CLAUDE.md` (and other tracked docs) must describe the project only —
  portable across any contributor's machine.
- Machine-specific quirks still need to be written down somewhere, or the
  next person to hit them re-diagnoses from scratch.
- A real PR review process (comment / approve / request changes) needs to
  exist, ideally with the option to enforce it technically.

### Constraints

Discovered while investigating enforcement options: RoWAS is a **private**
repository on GitHub's **Free** plan. Both the classic branch-protection API
(`/branches/main/protection`) and the newer rulesets API
(`/repos/.../rulesets`) return `403: "Upgrade to GitHub Pro or make this
repository public to enable this feature."` There is also currently only
one collaborator (`harvoline`, admin) — even with protection enabled,
GitHub does not allow a PR author to approve their own pull request, so a
"1 approval required" rule would deadlock a solo contributor's merges.

### Analysis

**For the portability problem:** considered (a) just deleting the
WSL-specific content, losing the diagnostic knowledge, versus (b) moving it
to a new file that is explicitly *not* part of the shared/portable
documentation set. Chose (b) — a gitignored `user-setup.md` at the repo
root, per the owner's suggestion, with `documentation-workflow.md` updated
to define this as a deliberate exception (per-machine, not synced, not
subject to the "update in the same PR" rule that governs every other doc).

**For the review process:** presented three enforcement options once the
platform constraint was known: (1) convention only — document the process,
no technical gate, free, but relies on discipline; (2) upgrade to GitHub
Pro/Team — real enforcement, has a cost, requires the owner's billing
action (not something to do unilaterally); (3) make the repo public —
free enforcement, but exposes proprietary code. Also asked separately
whether to add a PR template and CODEOWNERS regardless of which
enforcement path was chosen, since those improve review quality even
without a technical gate.

### Delegation

Not applicable.

### Decision

- `CLAUDE.md`'s WSL-specific bullet replaced with a generic instruction to
  check a local `user-setup.md`; the actual WSL content now lives there
  (gitignored, not tracked).
- `rules.md`, `coding-workflow.md`, and `README.md` had their
  environment-specific language generalized the same way.
- PR review: **convention only**, documented as a non-negotiable process
  rule in `rules.md` ("Pull Request Review") and detailed in
  `coding-workflow.md` ("Pull Requests") — Comment/Request changes/Approve
  via GitHub's native review UI, feedback addressed via follow-up commits,
  merge only after outstanding "Request changes" are resolved and at least
  one approval exists.
- Added `.github/pull_request_template.md` (summary, verification
  checklist, documentation checklist) and `.github/CODEOWNERS` (`* @harvoline`
  for now).

### Reasoning

The portability fix directly serves "maintainability" and "clarity" for
future contributors — a Mac/Linux developer reading a hardcoded WSL
workaround in `CLAUDE.md` would reasonably assume it applies to them, or
waste time figuring out that it doesn't.

Convention-only enforcement was the owner's explicit choice given the
platform limitation and solo-collaborator reality — upgrading the plan or
going public are both real options but are billing/visibility decisions
outside what should be assumed on the project's behalf. The PR
template/CODEOWNERS were added regardless of the enforcement decision
because they cost nothing and make review meaningful even without a
technical gate (a checklist plus explicit routing beats an ad hoc review).

### Implementation Order

1. Confirm enforcement options are actually blocked (checked the API
   directly rather than assuming) before presenting them as trade-offs.
2. Get the owner's decision on enforcement level and PR template/CODEOWNERS
   before making repo-wide changes.
3. Create `user-setup.md`, add it to `.gitignore`.
4. Strip machine-specific content from `CLAUDE.md`, `rules.md`,
   `coding-workflow.md`, `README.md`; add the generic "check user-setup.md"
   pointer in each.
5. Add the PR review process to `rules.md` and `coding-workflow.md`.
6. Add `.github/pull_request_template.md` and `.github/CODEOWNERS`.
7. Verify (`pytest`/`ruff`/`mypy`) still pass — none of this touched
   application code, but re-verified anyway rather than assuming docs-only
   changes can't break anything.

### Trade-offs

- **Pro:** shared docs are now genuinely portable; the diagnostic knowledge
  about the WSL quirk isn't lost, just relocated to where it belongs.
- **Con:** convention-only review enforcement means nothing technically
  stops a self-merge without review today. Accepted explicitly by the
  owner; the trigger conditions for revisiting are written down (`rules.md`,
  `CLAUDE.md` Known Decisions) so it isn't forgotten.

### Result

PR #1 updated in response to the owner's review comment. Review process
now has a documented, if not yet technically enforced, shape: template,
routing (CODEOWNERS), and an explicit comment/approve/request-changes cycle
described in `coding-workflow.md`.

### Future Considerations

Add real branch protection (required approvals, no direct pushes to
`main`, dismiss stale approvals on new commits) the moment either becomes
true: a second collaborator joins, or the plan is upgraded to Pro/Team.

---

## 5. Establishing the Multi-Agent Orchestrator Workflow

### Problem

All engineering work so far has gone through a single Claude Code session
with no structured way to guarantee that a given change was examined from
every relevant engineering angle (business, architecture, security,
performance, UX, etc.) rather than whichever angles happened to occur to
that one session. The project owner wants to keep talking to a single
Orchestrator, while trusting that important concerns won't be missed
because nobody thought to raise them.

### Context

The project owner supplied a detailed process specification (agent
hierarchy, coverage model, risk-based review levels, output contract,
synthesis/conflict-resolution process, approval boundaries) and explicitly
scoped the first task as establishing this workflow — not implementing
robot allocation logic.

### Requirements

- The project owner should only need to talk to one agent.
- Every meaningful requirement gets a conscious coverage assessment across
  a fixed list of engineering dimensions.
- Specialist involvement is selected per-requirement, not fixed.
- Parallel vs. dependent delegation must be explicit.
- Findings must be structured (Objective/Findings/Risks/.../Confidence) so
  they can be synthesized rather than just concatenated.
- No additional orchestration layer (sub-orchestrators) unless genuinely
  justified — and if not justified now, that absence must be explained,
  not just assumed.

### Constraints

- This project has no ticketing/requirements-tracking tool, one owner, one
  repository, and (as of this writing) zero business logic — any process
  introduced must be proportionate to that, not to a larger team.
- Must not implement robot allocation functionality as part of this task
  (explicit instruction).

### Analysis

Considered two implementation approaches for "specialist agents":

1. **Purely conceptual** — the Orchestrator mentally adopts each
   specialist's lens and writes prompts ad hoc when delegating to the
   generic `general-purpose`/`Explore` agents.
2. **Concrete, reusable subagent definitions** under `.claude/agents/`, one
   file per specialist role, each with a fixed focus, output contract, and
   restricted tool access — invoked by name via the `Agent` tool.

Chose (2): a fixed roster with a fixed output contract is more reliable at
guaranteeing "a concern doesn't get missed because nobody thought to ask
about it" than re-deriving a good prompt from scratch each time, which is
exactly the failure mode this whole workflow exists to prevent. The
specialist roster mirrors the project owner's own enumerated roles exactly
(Business, Domain, Architecture, Testing, Security, Performance, UX,
Documentation, DevOps, Production Readiness) rather than inventing new
ones — ten agents, matching ten genuinely distinct concerns, not padding
for the appearance of thoroughness ("no agent theatre").

Also considered whether specialists should be able to edit files directly
(e.g. `documentation-agent` drafting doc updates in place). Decided against
it project-wide: keeping all ten specialists read-only (plus non-destructive
`Bash` where a role needs to verify a real command, e.g. `testing-agent`
running `pytest`) means concurrent investigations can never collide on a
file edit, and the Orchestrator remains the single point of accountability
for what actually lands in the repo. Flagged as an open question in
`orchestrator-workflow.md` rather than treated as unquestionably settled.

Considered whether an "Implementation Agent" subagent should exist,
per the project owner's own role list. Decided against a separate
implementation subagent: this project's TDD discipline
(`testing-workflow.md`) depends on tight RED→GREEN→REFACTOR continuity,
and the project owner's own constraint on that role ("must not
independently override major architectural decisions") is trivially
guaranteed by not giving any subagent edit access, rather than by trusting
delegation boundaries to hold under a separate agent's judgment.

Considered whether "Devil's Advocate" needed its own persistent persona
file. Decided against it: a dedicated file would either duplicate an
existing specialist's focus or need to be deliberately generic, and the
project owner's own description of the role ("independent from the
original recommendation where possible") is better served by dynamically
picking whichever existing specialist is least invested in the original
recommendation, per requirement.

Considered whether to introduce a Master/Domain/Technical/Operations
orchestration layer now, since the project owner's spec describes one as a
future possibility. Rejected for now — documented explicitly in
`orchestrator-workflow.md` ("Why No Additional Orchestration Layer Now")
with the specific re-evaluation triggers, per the project owner's own
instruction not to add layers "merely because the architecture allows it."

### Delegation

None — this task was explicitly scoped to establish the workflow itself,
not to exercise it on a real requirement yet.

### Decision

- New `orchestrator-workflow.md` defining: roles, hierarchy, coverage
  model, risk-based review levels (1-4, calibrated with this project's own
  examples), the Orchestrator/specialist boundary, the agent output
  contract, synthesis process, conflict resolution, requirements
  traceability, Definition of Done additions, TDD/post-implementation
  review integration, decision documentation (reusing `solutions.md`, no
  new file), limitations of the architecture, and explicit "no additional
  layer yet" reasoning.
- Ten new specialist subagent definitions under `.claude/agents/`:
  `business-agent`, `domain-agent`, `architecture-agent`, `testing-agent`,
  `security-agent`, `performance-agent`, `ux-agent`,
  `documentation-agent`, `devops-agent`, `production-readiness-agent` — all
  read-only (plus scoped non-destructive `Bash` for the roles that need to
  verify something real), all following the same output contract.
- `documentation-workflow.md`, `README.md`, `CLAUDE.md`, and `rules.md`
  updated with pointers to the new file/directory, without duplicating
  content that already lives in `rules.md` (approval boundaries) or
  `solutions.md` (decision-record format).

### Reasoning

Every design choice above traces back to the project owner's own stated
principle: coverage is mandatory, agent participation is optional. A fixed,
reusable roster with a fixed output contract makes "was this concern
considered" answerable and auditable, rather than dependent on whichever
prompt the Orchestrator happened to write in the moment. Declining to add a
new orchestration layer, a dedicated Implementation agent, or a dedicated
Devil's Advocate agent all follow the same "no agent theatre" instruction:
each of those would have added structure without solving a coordination
problem that actually exists yet at this project's current size (one
owner, one repo, no business logic).

### Implementation Order

1. Reviewed all existing project documentation (`CLAUDE.md`, `rules.md`,
   `README.md`, `coding-workflow.md`, `testing-workflow.md`,
   `documentation-workflow.md`, `app-workflow.md`, `solutions.md`,
   `tools.md`) to ground the new workflow in what already exists rather
   than duplicating or contradicting it.
2. Wrote `orchestrator-workflow.md`.
3. Wrote the ten specialist agent definitions.
4. Cross-linked the new file/directory from every doc whose own "when to
   update" trigger table required it.
5. Logged this decision here and in `tools.md`.

### Trade-offs

- **Pro:** the project owner's stated coverage principle now has a
  concrete mechanism (fixed roster + coverage assessment + output
  contract) rather than remaining a purely aspirational instruction.
- **Con:** ten specialist files are more to maintain than zero — mitigated
  by most of them being genuinely reusable across any future requirement,
  and by three of the ten (`devops-agent`, `production-readiness-agent`,
  and to a lesser extent `security-agent`) being explicitly documented as
  currently dormant/low-signal until the project has CI/CD, a deployed
  system, or external input, respectively.
- **Con:** read-only specialists mean every specialist finding still has
  to pass through the Orchestrator to become a file change — a
  deliberate bottleneck, accepted because it keeps a single point of
  accountability for what lands in the repo.

### Result

A working, documented multi-agent delegation model exists and is ready to
be exercised on the first real requirement. No business logic was
implemented, per the explicit scope of this task.

### Future Considerations

- Re-evaluate the read-only specialist boundary if it becomes a genuine
  bottleneck (see `orchestrator-workflow.md` "Open Questions").
- Re-evaluate whether `devops-agent`/`production-readiness-agent` are
  pulling their weight once CI/CD or a deployed system exists.
- Re-evaluate the "no additional orchestration layer" decision against the
  specific triggers documented in `orchestrator-workflow.md`, not on a
  fixed schedule.


---

## Level 1 everbot port (package rename + src-layout)

### Problem

PR #3 (`TR02_LEVEL_1`) delivered Level 1 behaviour with a flat `everbot/` package
at the repo root and a pytest-only `requirements.txt`, diverging from main's
src-layout + `pyproject.toml` tooling (`pip install -e ".[dev]"` with pytest,
ruff, mypy strict).

### Decision

- Keep main's packaging: **src-layout** under `src/everbot/`, `pyproject.toml`
  entry point `everbot.cli:main`, mypy/ruff pointed at `src`.
- Port Level 1 modules, tests, and domain docs (`robots.md`, `features/level-1.md`)
  from `origin/TR02_LEVEL_1`.
- Retain the strategy pattern (Allocator + AllocationStrategy +
  CategoryDistributionStrategy).
- Remove the scaffolding package `src/robot_allocation/` after migration —
  single package tree only.
- Open a **new** PR off main; do not close PR #3 (this supersedes its packaging
  approach while preserving Level 1 behaviour).

### Reasoning

Owner decided the product package name is `everbot`, and main's tooling is the
canonical foundation. Merging PR #3 as-is would regress packaging; re-porting
onto main preserves both the Level 1 algorithm/tests and the engineering
scaffold.

### Result

`src/everbot/` with Level 1 allocation, updated README/CLAUDE/solutions, domain
docs from PR #3, and a green pytest/ruff/mypy suite under `pip install -e ".[dev]"`.

---

## Level 2 — Cost Optimised Allocation

### Problem

Level 2 must minimise charging cost without Level 1's mandatory diversity, expose
an L1 vs L2 cost comparison in the CLI, and uniquely match the owner's worked
examples (including Example 2 where 2 Bravo @ $4 beats 1 Delta @ $4).

### Decision

- New ``CostOptimisedStrategy`` registered as ``STRATEGY_BY_LEVEL[2]``.
- Lexicographic objective: **min cost → min excess → fewest robots → prefer more
  Delta then Charlie**. Excess before fewest-robots is required so Example 2
  uniquely selects Bravo:2 (exact 6h) over Delta:1 (8h, same $4, fewer robots).
- ``compare_levels()`` always runs Level 2; Level 1 is best-effort. If Level 1
  raises (e.g. missing category), the CLI still shows Level 2 and reports Level 1
  infeasible rather than failing the run.
- CLI header wording keeps the owner's US spelling ("Cost Optimized Allocation");
  the strategy class uses UK spelling consistent with existing "Minimise" docs
  (``CostOptimisedStrategy``).

### Reasoning

Open/Closed: Level 1 ``CategoryDistributionStrategy`` is untouched. Shared
validation stays in ``Allocator``. Bounded triple-loop search mirrors Level 1
and is trivial at realistic inventory sizes.

### Result

Level 2 examples + comparison tests pass; existing Level 1 tests remain green.

## Level 3 — Standby Robot Activation + top-level menu

### Problem

Level 3 must recommend additional standby robots when active capacity cannot cover
requested hours, without a standby inventory prompt, while keeping Level 1 and
Level 2 behaviours available and uncollided behind a menu.

### Decision

- New workflow module ``standby.plan_standby`` / ``StandbyPlan`` (not an
  ``AllocationStrategy``) — Level 3 is capacity + optional shortfall fill, not a
  replacement inventory allocator.
- Shortfall fill reuses Level 2's lexicographic objective via
  ``CostOptimisedStrategy`` with unbounded caps (enough robots to cover shortfall
  + margin).
- Full active capacity is always applied first; additional section omitted when
  ``active_capacity >= requested``.
- CLI menu dispatches to ``run_level_1`` / ``run_level_2`` / ``run_level_3``.
- Additional lines coloured by robot type (Bravo blue, Charlie magenta, Delta
  yellow); colour off by default for tests, on for TTY in ``main``.

### Reasoning

Keeping ``AllocationStrategy`` for L1/L2 preserves Open/Closed for inventory-based
allocation. Standby activation is a different workflow (active capacity first,
unbounded recommend-to-buy), so a dedicated module avoids bending the strategy
interface. Separate runners prevent L1/L2/L3 output and validation paths from
colliding.

### Result

Owner example (1/1/1 active, 21h -> Charlie:1 @ $3) and no-additional-when-covered
cases pass; existing Level 1/2 tests remain green via their runners / menu paths.

## Level 4 — Multi-Client Allocation

### Problem

Level 3 served exactly one client. The owner's Level 4 requirement is "Level 3 +
multi-client": accept several client working-hour values on one input line
(single, comma-separated, or space-separated), prioritise by highest hours
requested, and list the standby robots needed when active robots fall short.

### Coverage assessment

Delegation to the specialist roster was **not** used for this change; the
reasoning per `orchestrator-workflow.md` ("coverage is mandatory, participation
is optional") is recorded here rather than left silent.

| Dimension | Status |
|---|---|
| Business / Requirements | Owner answered directly ("level 4 = level 3 + improvement"); the one genuinely open point — how the shared pool behaves — was decided from `robots.md`'s once-per-day rule, not invented |
| Domain / Data | Relevant. One new entity pair (`ClientPlan`, `MultiClientPlan`); no change to `Robot`, `Allocation`, or the error hierarchy |
| Architecture | Relevant. Mirrors the Level 3 precedent (workflow module, not an `AllocationStrategy`); no new dependency, no structural change |
| Testing | Relevant. Normal/edge/invalid breakdown written before implementation (see `testing-workflow.md`) |
| CLI / UX | Relevant. New prompt wording matches the owner's `Client working hours:` sample; menu grows to four options |
| Security | Low. One new input string, parsed with an explicit whitelist (integers only) and the existing validators; no new trust boundary, dependency, or data flow |
| Performance | Low. The per-client search is the same bounded triple loop as Level 2, run once per client; input sizes are terminal-typed |
| Documentation | Relevant. Handled in this change (`features/level-4.md`, `app-workflow.md`, `robots.md`, `README.md`, `CLAUDE.md`, `testing-workflow.md`, `tools.md`) |
| CI/CD / Ops | Not relevant. Deferred by standing decision; nothing here revisits it |
| Production readiness | Not relevant. No deployed system |
| Regression risk | Contained: Levels 1–3 behaviour is unchanged except the menu error string, which its test now asserts in the new form |

### Decision

- New workflow module `multiclient.py` (`plan_multi_client` / `MultiClientPlan` /
  `ClientPlan`), following the Level 3 precedent rather than adding an
  `AllocationStrategy` — Level 4 is a scheduling pass over several requests, not a
  single-inventory allocation algorithm.
- `parse_client_hours` lives in the domain, not the CLI: "how many clients does
  this input describe" is a business rule, and it keeps the terminal layer thin.
- **Shared pool, whole-robot consumption.** Clients are served in descending hours
  (ties by input order). If the remaining pool covers a client, it takes a
  cost-optimised subset of those robots (Level 2 objective); otherwise it takes
  every remaining robot and its shortfall goes to the Level 3 unbounded standby
  fill. A robot assigned to a client is spent for the day, so its unused hours are
  excess rather than credit for the next client.
- Clients keep their **input position** as their label while being served in
  priority order, so the output is traceable back to what was typed.
- `Allocator._validate_hours` / `_validate_inventory` became public
  (`validate_hours` / `validate_inventory`), and `standby._fill_shortfall` became
  `fill_shortfall`. Level 4 is the second real caller — the trigger the project's
  "no premature abstraction" rule asks for — and `standby.py` was already reaching
  into the private names.

### Reasoning

Hours-only drawdown (tracking the pool as a single number, as Level 3 does) was
rejected: it lets one Delta's day be split between two clients, contradicting
`robots.md`. Evaluating every client against the full inventory independently was
also rejected: it makes "prioritise by highest hours" allocatively meaningless,
since nothing is contended. Greedy highest-first is what the requirement states,
so it is implemented literally rather than replaced with a global optimisation
over all clients.

### Trade-offs

- Greedy service order can cost more overall than a globally optimised split
  across clients — accepted, because the priority rule is the requirement.
- A client that only needs a few hours can consume a Delta and leave nothing for
  the next client. That is the domain rule, and the test
  `test_assigned_robot_is_consumed_not_split_across_clients` pins it.
- `MultiClientPlan` exposes totals (`total_standby_cost`, `total_requested_hours`)
  that only the CLI currently uses; kept because they are one-line derived
  properties, not a new abstraction layer.

### Result

`features/level-4.md` spec, `multiclient.py`, menu option 4 with `run_level_4`,
and 43 new tests. Full suite 137 passed, `ruff check .` clean, `mypy src` (strict)
clean. The owner's `12,16,17,10,21` example produces the documented plan with a
$23 total standby cost, verified by running the CLI end to end.

### Future Considerations

If standby ever gains a real stock limit, the unbounded fill and the "insufficient
capacity cannot arise" note in `features/level-4.md` both need revisiting. If
allocation quality across clients ever matters more than the stated priority rule,
the greedy loop is the single place to replace.

## 2026-09-08 - CLI termination and review follow-ups

### Problem and decision

EOF and Ctrl+C escaped the terminal boundary as tracebacks. Handle only
`EOFError` and `KeyboardInterrupt` in `cli.main`: EOF prints
`Error: Input ended before allocation completed.` to stderr and returns 1;
interruption prints `Allocation cancelled.` to stderr and returns 130.
Both executable entry points already call this boundary. Reusable runners retain
their existing exception behaviour. No allocation rules or dependencies change.

### Coverage assessment

| Dimension | Assessment and ownership |
|---|---|
| Business / domain | Existing rules retained; no new allocation requirement |
| Architecture / maintainability | Main reviewer: one CLI-boundary handler avoids repeated catches |
| Testing / regression / edge cases | Main reviewer: failing tests first, menu and all four levels, subprocess EOF checks |
| CLI / error handling | Main reviewer: stderr, explicit exits, no traceback, restart after termination |
| Security | Main reviewer: no new input sink or dependency; catch only expected termination exceptions |
| Performance | Existing cubic search and numeric-bound issues documented, not changed |
| Documentation | Read-only specialist checked remaining agent/documentation drift; main reviewer owns edits |
| Git / operations | Working branch retained; no commit, publication, or CI change requested |
| Production readiness / technical debt | Local CLI reliability improved; installed-wheel verification remains open |

Specialist investigation was limited to documentation drift: the code change is
small and the main reviewer can verify all runtime dimensions directly.

### Alternatives and trade-offs

Catching in every runner duplicates policy and misses menu input. Catching all
exceptions would hide programming defects. A retry loop adds interaction policy
outside this fix. Handling expected termination once keeps domain services free
of terminal concerns. Existing domain-error output remains unchanged.

### Clarification of review issue 5: integer overflow

Python integers can represent `10**310`, and the positive-integer validator
accepts it. However, `ceil(hours / robot.hours)` performs `/` first, creating a
floating-point result. Floats have a finite range (about `1.8e308`), so that
division can raise `OverflowError` before `ceil` runs. For example,
`plan_standby({}, 10**310)` currently fails inside standby search-bound creation.
The same calculation exists in both allocation strategies.

This is a numerical implementation limit, not a negative/non-integer input error.
It is unlikely for normal manually entered requests, but contradicts accepting
arbitrarily large positive integers without a documented numerical limit.
For positive integers, `(hours + robot.hours - 1) // robot.hours` computes the
ceiling exactly without a float; retain the existing `+ 1` search margin after it.
This recommended change is not implemented in this task.

Integer division only fixes bound arithmetic. It does not make a search over
astronomical counts feasible. Search optimisation and a deliberate supported-scale
policy need separate consideration; no business input maximum was invented here.

### Updated review assessment

Earlier Level 2/4 records treated terminal-sized searches as low risk. A review
probe of `fill_shortfall(1000)` took about 3.5 seconds, so those historical
assessments do not establish current scalability. Cubic growth, numeric overflow,
the setuptools minimum/SPDX mismatch, and installed-package verification are
open items in README's Technical Debt. Source tests alone cannot close them.

Documentation now distinguishes strategies from workflows, removes obsolete
foundation-state claims from current guides, and keeps README concise. Historical
decision entries above retain their original context.

## 2026-09-08 - Optional advanced reporting

### Decision and assumptions

Owner approved menu option 5, active-plus-standby planned totals, aggregate
requested/assigned capacity utilization, active inventory usage by count and
percentage, and estimated useful-capacity utilization by type. Allocation keeps
cost, excess, then robot-count priorities. Useful hours are attributed
proportionally within each client, not by inventing a robot execution order.
`advanced.py` composes the unchanged Level 4 service and uses standard-library
Fraction for exact attribution until display. Zero type denominators show N/A;
aggregate assigned capacity is always positive for validated nonempty requests.

### Coverage assessment

| Dimension | Assessment |
|---|---|
| Business/domain | Owner clarified totals and utilization; formulas in optional feature spec |
| Architecture/maintainability | Separate summary service and CLI runner; reuse Level 4 unchanged |
| Testing/regression | Failing tests first; exact totals, per-client attribution, weighted aggregation, zero stock, invalid input and menu termination |
| UX | Planned totals, active/standby subtotals, estimated metric labels, N/A denominators |
| Security | Existing numeric validation; no new dependencies, persistence or external sinks |
| Performance | One additional pass over clients and types; Fraction arithmetic can grow with varied denominators; existing allocation search limits remain |
| Documentation | Feature spec, README, application flow, context, testing guide and tool log updated |
| Ops/production | Local CLI only; CI remains deferred; no commit, push or PR authorized |
| Independent review | Read-only reviewer checked implementation and identified attribution-test gaps, now covered |

Other specialist delegation was unnecessary: this reporting layer reuses existing
allocation and validation, and the main reviewer covered the bounded change.

### Trade-offs

Proportional useful hours are a planning estimate, not measured runtime. Fractions
avoid rounding accumulation; formatting rounds percentages to two decimal places.
Active inventory excludes standby because standby stock has no finite denominator.
No global allocation optimization, new input syntax, or large-input fixes are added.
