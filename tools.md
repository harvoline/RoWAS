# AI Tool Usage Log

Record of meaningful AI-assisted development activity on this project, kept
for transparency and auditability. Not every trivial interaction is logged —
only usage that materially shaped the codebase or a decision.

---

## 2026-09-05 — Foundation Setup

**Tool used:** Claude Code (Claude Sonnet 5), operating per the project's
`CLAUDE.md`-style instructions provided by the project owner.

**Purpose:** Establish the engineering foundation for an empty repository
before any business functionality is implemented — project structure, tech
stack selection, documentation system, testing/lint/type-check tooling, and
process rules.

**Input/context provided:** A detailed process specification (role,
documentation requirements, TDD mandate, git workflow rules, CI/CD deferral
instructions, and an explicit "do not implement business logic yet"
constraint). The repository itself was empty (one empty initial commit, no
files besides an ignored `.claude/settings.local.json`).

**What the tool did:**

1. Inspected the repository and discovered a DevSwarm-specific environment
   issue: the `.git` file is a worktree pointer to a WSL-only path
   (`/var/www/rows`), which native Windows git cannot resolve. Diagnosed by
   comparing against sibling DevSwarm repos (same pattern in all of them,
   ruling out corruption) and confirming via `wsl.exe` that the real git
   history is reachable from WSL. This finding is recorded in `solutions.md`
   and `CLAUDE.md`.
2. Asked the project owner to choose a language/runtime (a decision that
   could not be reasonably inferred and materially affects architecture,
   testing, and tooling). **Result:** Python was selected from a shortlist
   of TypeScript, Python, Java, and C#.
3. Scaffolded a src-layout Python package (`src/robot_allocation/`), a
   pytest test suite, and `pyproject.toml` covering packaging, pytest,
   ruff, and mypy(strict) configuration.
4. Followed TDD for the scaffolding itself: wrote `tests/test_cli.py`
   first, confirmed it could not pass (package did not exist yet), then
   added the minimal `cli.py` implementation.
5. Verified the environment for real: created a virtualenv inside WSL,
   installed the project in editable mode with dev dependencies, and ran
   `pytest`, `ruff check .`, and `mypy src` — all passed (1 test, 0 lint
   issues, 0 type errors). Commands and output were inspected directly, not
   assumed.
6. Wrote the full documentation set required by the project instructions:
   `CLAUDE.md`, `rules.md`, `testing-workflow.md`, `coding-workflow.md`,
   `documentation-workflow.md`, `app-workflow.md`, `solutions.md`, and
   `README.md`.

**Accepted / rejected / modified:** Pending project owner review (this is
the first deliverable of the session). No prior output existed to accept or
reject.

**Limitations / risks discovered:**

- `ensurepip` is not installed in the WSL Ubuntu-20.04 environment, so
  `python3 -m venv` cannot create a venv with pip pre-seeded. Worked around
  using `pip install --python <venv-python> ...` from the already-present
  user-level pip, rather than requesting `sudo apt install
  python3.10-venv` (which would have required a password and a
  system-level change outside this repository's scope). This workaround is
  reproducible but slightly non-standard — a developer setting this up
  fresh on a machine with a normal Python install (with `ensurepip`
  available) will not need it.
- No remote git repository is configured, and CI/CD is explicitly
  undecided — both are flagged as open items rather than resolved by the
  AI, per the project's instruction to defer CI/CD decisions to a later
  checkpoint.

---

## 2026-09-05 — Remote Configuration and PR Creation

**Tool used:** Claude Code, via `gh` CLI (GitHub) and `git`, both invoked
through WSL for the reasons recorded in `solutions.md` §2.

**Purpose:** Wire up the GitHub remote the project owner provided
(`harvoline/RoWAS`), push the foundation work, and open the first PR for
review — while resolving the CI/CD checkpoint along the way.

**What happened:** Verified the remote was reachable and empty before
touching it, confirmed the specific push/PR plan with the owner, then
pushed `main` and `initial-setup` and opened PR #1 via `gh pr create`.

**Limitation/risk discovered:** `gh pr create --body "$(cat <<'EOF' ... EOF)"`
run through a nested `bash -c` (this tool's shell -> `wsl.exe` -> WSL bash)
had its heredoc quoting broken — backtick-wrapped code spans in the PR body
(e.g. `` `pytest` ``) were evaluated as command substitution by an
intermediate shell and silently vanished from the body, and the shell also
tried to execute `pytest`/`ruff`/`mypy` as commands (all "not found", since
they only exist inside the project's venv). **Not accepted as-is** — caught
by reviewing the created PR's actual body via `gh pr view --json body`
rather than trusting the create command's apparent success. **Fixed** by
writing the body to a plain file with the `Write` tool (no shell escaping
involved) and applying it with `gh pr edit --body-file`. Lesson recorded in
`solutions.md`: any multi-line or backtick-containing text destined for a
shell command in this environment should go through a file, not inline
heredoc/quoting, when the command crosses the Windows-shell/WSL boundary.

---

## 2026-09-05 — Responding to PR #1 Review Feedback, Establishing Review Process

**Tool used:** Claude Code, via `gh api` (to inspect PR review comments and
check branch-protection/rulesets availability) and `git`/`gh` (to commit and
push the fix).

**Purpose:** Act on the owner's inline PR review comment (CLAUDE.md
shouldn't contain machine-specific WSL detail) and their separate request
for a "proper team flow" with commentable/approvable/rejectable PRs.

**What the tool did:** Fetched the actual review comment text via
`gh api repos/.../pulls/1/comments` rather than assuming its content from
the PR diff. Checked real GitHub API responses for branch protection and
rulesets before proposing any enforcement approach — both returned
403 (Free-plan/private-repo restriction) — rather than assuming they'd be
available. Presented the resulting trade-offs (convention-only vs.
paid-upgrade vs. public) to the owner instead of picking one.

**Accepted / rejected / modified:** Owner selected "convention only, no
technical gate" for enforcement, and "yes, add both" for PR
template + CODEOWNERS. Implemented as specified — see `solutions.md` §4.

**Limitations discovered:** GitHub's branch-protection and rulesets APIs
are both unavailable for private repositories below the Pro tier — this
wasn't previously known and materially changed what "proper team flow"
could mean technically (process discipline now, technical gate later).

---

## 2026-09-06 — Establishing the Multi-Agent Orchestrator Workflow

**Tool used:** Claude Code, operating per a detailed multi-agent process
specification provided by the project owner (Orchestrator role, specialist
roster, hierarchy, coverage model, risk-based review levels, output
contract, synthesis/conflict-resolution process, approval boundaries).

**Purpose:** Establish the multi-agent delegation workflow itself — no
robot allocation functionality was in scope for this task, by explicit
instruction.

**What the tool did:**

1. Rediscovered the DevSwarm/WSL git environment mismatch documented in
   `solutions.md` §2 (this workspace's branch was still pinned to the
   repository's pre-foundation commit) and fast-forwarded it to the current
   `origin/main` via WSL, per the already-recorded fix — no `.git` internals
   were touched, consistent with `rules.md` "Safety."
2. Read the full existing documentation set before designing anything, to
   avoid contradicting established conventions.
3. Authored `orchestrator-workflow.md` defining the Orchestrator/specialist
   boundary, coverage model, four risk-based review levels (calibrated
   with this project's own examples), the agent output contract, synthesis
   and conflict-resolution processes, and explicit reasoning for *not*
   introducing an additional orchestration layer yet.
4. Authored ten read-only specialist subagent definitions under
   `.claude/agents/` (`business-agent`, `domain-agent`,
   `architecture-agent`, `testing-agent`, `security-agent`,
   `performance-agent`, `ux-agent`, `documentation-agent`, `devops-agent`,
   `production-readiness-agent`), each scoped to the project owner's own
   enumerated specialist roles, each following the same structured output
   contract.
5. Cross-linked the new file/directory from `documentation-workflow.md`,
   `README.md`, `CLAUDE.md`, and `rules.md`, without duplicating content
   that already lives in `rules.md` (approval boundaries) or `solutions.md`
   (decision-record format).
6. Logged the full reasoning in `solutions.md` §5, including the
   alternatives considered and rejected (editable specialists, a separate
   Implementation agent, a dedicated Devil's Advocate persona, an
   additional orchestration layer).

**Accepted / rejected / modified:** Pending project owner review — this is
a process/documentation deliverable, no code was changed, and no commit was
made without explicit instruction (per this session's operating rules).

**Limitations / risks discovered:** none new beyond what's already recorded
in `orchestrator-workflow.md` "Limitations and Risks of This Architecture"
— notably that nothing technically enforces the Orchestrator actually
running the coverage assessment before implementing (same category of gap
as the already-accepted convention-only PR review).

---

## 2026-09-08 — Level 4 Multi-Client Allocation

**Tool used:** Claude Code (Claude Opus 5), acting as Orchestrator per
`orchestrator-workflow.md`.

**Purpose:** Implement Level 4 — several clients served from one active robot
inventory, prioritised by highest hours requested, with standby recommendations
for whatever the pool cannot cover.

**Input/context provided:** The owner's Level 4 requirement text with three
sample input forms, followed by the clarification "level 4 = level 3 +
changes / improvement — previously only 1 working [hours] allowed", and an
explicit instruction not to commit, push, or open a PR.

**What the tool did:**

1. Read the full rule/workflow/spec/code set before proposing anything, and
   confirmed a green baseline (94 tests, ruff, mypy strict) before changing code.
2. Asked one blocking question — how the shared pool behaves across clients —
   and, when the owner declined to re-litigate Level 3, resolved it from
   `robots.md`'s once-per-day rule (whole-robot consumption) and stated the
   assumption instead of asking again.
3. Wrote `features/level-4.md` first, including a worked example whose numbers
   were verified numerically before being written down.
4. Followed TDD: `tests/test_multiclient.py` (RED, module absent) → `multiclient.py`
   (GREEN) → CLI tests (RED) → menu option 4 + `run_level_4` (GREEN) → refactor
   (Levels 3 and 4 now share one standby-line renderer).
5. Promoted `Allocator.validate_hours` / `validate_inventory` and
   `standby.fill_shortfall` from private to public, Level 4 being the second real
   caller and `standby.py` having already reached into the private names.
6. Ran the CLI end to end on the owner's `12,16,17,10,21` example to confirm the
   rendered output matches the spec, rather than trusting the tests alone.
7. Recorded the coverage assessment — including why no specialist subagent was
   delegated to — in `solutions.md`, and refreshed the stale "Current State"
   section of `testing-workflow.md`.

**Accepted / rejected / modified:** Pending project owner review. Nothing was
committed, pushed, or opened as a PR, per the owner's explicit instruction; the
work sits uncommitted on `TR05_LEVEL_4`.

**Limitations / risks discovered:**

- Greedy highest-hours-first service can cost more in total standby than a
  globally optimised split across clients. This is the stated requirement, not a
  defect, and is recorded as a trade-off in `solutions.md`.
- The menu's invalid-choice message changed from "1, 2, or 3" to "1, 2, 3, or 4";
  its existing test was updated deliberately, which is the only Level 1–3
  behaviour touched by this change.

