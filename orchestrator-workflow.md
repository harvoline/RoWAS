# Multi-Agent Orchestrator Workflow

This document defines how multi-agent delegation works on this project. It
exists so that the project owner only ever has to talk to one thing — the
Orchestrator — while still getting broad engineering coverage on every
change. It does not replace `coding-workflow.md`, `testing-workflow.md`, or
`rules.md`; it sits above them, deciding *who* investigates a requirement
before those other documents' processes (TDD, branching, review) take over.

## Core Principle

> Coverage is mandatory. Agent participation is optional.

Every meaningful engineering dimension (business, domain, architecture,
testing, security, performance, UX, documentation, operations, production
readiness) must be **consciously evaluated** for every meaningful change.
Not every dimension needs its own specialist investigation — most don't, for
most changes. The Orchestrator must always be able to say, for any dimension
it didn't delegate, *why* it judged that dimension low-relevance, not just
that it wasn't mentioned.

This is not about using more agents. It's about not letting a concern get
missed because nobody thought to look at it.

## Roles

### Orchestrator

The Orchestrator is the primary Claude Code session (the agent the project
owner is talking to directly). It:

- Interprets the project owner's intent.
- Runs the coverage assessment (below) for every meaningful requirement.
- Selects the minimum set of specialists needed for sufficient coverage.
- Decides what can run in parallel vs. what depends on another agent's
  findings.
- Synthesizes specialist findings into one coherent recommendation.
- Owns all actual file edits, test-writing, and commits — specialists
  investigate and recommend, they do not implement (see "Implementation",
  below).
- Surfaces conflicts, risks, and assumptions rather than resolving them
  silently.
- Enforces the approval boundaries in `rules.md` before acting on anything
  that requires the project owner's sign-off.

### Specialist Agents

Ten specialist roles exist as real, invocable subagents in
`.claude/agents/`, one file per role. The Orchestrator invokes them via the
`Agent` tool by name (`subagent_type`) with a specific, self-contained
question — never "review this feature" (see `rules.md`-style reasoning in
each agent file for why vague briefs are rejected).

| Agent file | Role | Focus | Typical trigger |
|---|---|---|---|
| `business-agent` | Business / Requirements | Ambiguities, missing requirements, acceptance criteria, business edge cases | Any new or changed business rule |
| `domain-agent` | Domain / Data | Entities, relationships, invariants, data structures, domain boundaries | New or changed domain model / state |
| `architecture-agent` | Architecture | Component boundaries, separation of concerns, dependencies, extensibility | New module, new dependency, structural change |
| `testing-agent` | Testing / QA | Test strategy, edge/boundary/invalid/failure cases, coverage gaps, regression risk | Any change with observable behaviour |
| `security-agent` | Security | Input validation, trust boundaries, injection risk, dependency risk, data exposure | New external input, new dependency, new data flow |
| `performance-agent` | Performance | Complexity, memory, I/O, scalability, bottlenecks | Allocation/algorithmic logic, large-data handling |
| `ux-agent` | CLI / UX | Terminal I/O clarity, error messages, help text, usability | Any change to CLI input/output/help |
| `documentation-agent` | Documentation | README, workflow docs, decision records, handover quality | Any change requiring doc updates per `documentation-workflow.md` |
| `devops-agent` | DevOps / Operations | Build, CI/CD, environment config, monitoring, release strategy | Only if the CI/CD-deferred decision in `rules.md` is revisited, or packaging/build changes |
| `production-readiness-agent` | Production Readiness | Reliability, failure modes, observability, recovery, operational complexity | Level 3–4 changes only (see Review Levels) |

Every specialist file follows the same output contract (below) and is
**read-only by design** — they get `Read`, `Grep`, `Glob`, and (where their
role needs to actually run something to verify a claim, e.g. `testing-agent`
running `pytest`) `Bash` restricted to non-destructive verification
commands. None of them get `Edit`/`Write`. This is deliberate: it keeps
concurrent investigations from stepping on each other's file changes, and it
keeps the actual implementation decision with the Orchestrator, who has full
conversation context and is accountable for what lands in the repo.

### Implementation

There is no separate "Implementation Agent" subagent file in this project.
The Orchestrator implements directly, for two reasons:

1. TDD discipline (`testing-workflow.md`) requires tight RED→GREEN→REFACTOR
   continuity — handing implementation to a separate agent per cycle would
   fragment that loop for no benefit at this project's current size.
2. The framework's own rule for the Implementation role ("must not
   independently override major architectural decisions") is easiest to
   guarantee by not giving a separate agent edit access at all, rather than
   by trusting a delegated agent to respect that boundary.

If the project grows enough that parallel implementation work is genuinely
needed (see "Why No Additional Orchestration Layer Now"), this should be
revisited — not assumed away permanently.

### Devil's Advocate

Not a fixed persona. For Level 3–4 changes, the Orchestrator assigns the
challenge role to whichever existing specialist is most independent of the
original recommendation (e.g. if `architecture-agent` proposed a design,
`testing-agent` or a fresh `general-purpose` agent challenges it), with an
explicit brief to find reasons it could fail — never to confirm it. See
"Conflict Resolution" below for what happens when the challenge surfaces a
real disagreement.

## Agent Hierarchy

```
Human (project owner)
  │
  ▼
Orchestrator (this Claude Code session)
  │
  ▼
Specialist Agents (.claude/agents/*.md, invoked via the Agent tool)
```

No sub-orchestrators or domain/technical/operations orchestration layer
exists, and none should be added right now. See "Why No Additional
Orchestration Layer Now."

## Coverage Model

For every meaningful requirement, the Orchestrator evaluates each dimension
below as: **Relevant / Not relevant / Already covered / Requires specialist
review / Requires human decision / Requires further investigation**.

```
Business / Requirements     Error Handling            CLI / UX
Domain / Data Model         Security                  Documentation
Architecture / Design       Performance                Git / Change Mgmt
Implementation              Edge Cases                CI/CD / Operations
Testing / QA                Maintainability           Regression Risk
Production Readiness        Technical Debt
```

For non-trivial changes, this is written out as a coverage matrix (see
`solutions.md` for the format — reuse the table style already established
there rather than inventing a new one).

## Risk-Based Delegation → Review Levels

Assessed dimensions: Impact, Complexity, Uncertainty, Failure Cost, Change
Surface, Regression Risk, Security Risk, Performance Risk. These map to four
review levels. Examples below are calibrated to *this* project (a CLI robot
allocation system with no business logic yet):

**Level 1 — Small Change.** Typo, doc-only edit, CLI wording tweak,
formatting. Workflow: Orchestrator → one relevant specialist (usually
`ux-agent` or `documentation-agent`) → done. No coverage matrix needed.

**Level 2 — Normal Feature.** A new CLI flag, a new validation rule, a
single well-scoped business rule once requirements arrive. Workflow:
Orchestrator → `business-agent`, `architecture-agent`, `testing-agent`,
`ux-agent` (parallel, since none depend on another's findings for a
well-scoped change) → synthesis → implementation → QA pass.

**Level 3 — Significant Feature.** The first real allocation algorithm, a
new persistence layer, multi-rule priority logic. Workflow: Orchestrator →
`business-agent` → `domain-agent` (depends on business findings) →
`architecture-agent` (depends on domain model) → `security-agent` +
`performance-agent` + `testing-agent` + `ux-agent` (parallel once the design
is stable) → synthesis → Devil's Advocate challenge → implementation →
independent post-implementation review.

**Level 4 — Critical Change.** Data migration, a business-rule reversal
after the system holds real data, anything touching production
infrastructure once this system has any. Workflow: everything in Level 3,
plus explicit human approval before implementation begins (not just before
merge), and `production-readiness-agent` review after implementation.

Nothing in this project has reached Level 3–4 yet — there is no business
logic. This section exists so the escalation path is defined *before* it's
needed.

## Boundary Between Orchestrator and Specialists

- Specialists **investigate and recommend**. They read code/docs, run
  non-destructive verification commands, and return structured findings.
- Specialists **do not** edit files, run tests destructively, install
  packages, touch git, or make the final call.
- The Orchestrator **synthesizes, decides, implements, tests, and commits**.
- If a specialist's findings imply a file change, the Orchestrator makes
  that change itself (or explicitly hands it to a fresh implementation pass)
  — a specialist recommending a fix is not the same as the fix landing.

## Agent Output Contract

Every specialist response — and every Orchestrator synthesis pass reading
one — must be structured as:

```
Objective / Findings / Requirements / Risks / Edge Cases / Assumptions /
Recommendations / Alternatives / Trade-offs / Questions / Confidence
(High/Medium/Low) / Handoff
```

Findings must cite actual files, functions, tests, or config where the
repository can be inspected — not vague claims. Confidence must be
explicit; "Low" confidence findings get flagged in synthesis, not quietly
treated as settled.

## Synthesis Process

The Orchestrator never concatenates specialist responses. It produces:

```
Requirement Understanding / Coverage Assessment / Findings / Agreements /
Conflicts / Risks / Edge Cases / Assumptions / Proposed Solution /
Alternatives / Trade-offs / Testing Strategy / Documentation Impact /
Decision Required / Recommendation
```

This is the format the project owner should expect to see for any Level
2+ change before implementation starts.

## Conflict Resolution

1. Identify the disagreement explicitly — do not average or pick a side
   silently.
2. Present both positions and their reasoning.
3. Check against the actual requirement, existing architecture
   (`CLAUDE.md`), and project rules (`rules.md`).
4. If evidence resolves it, say so and explain why.
5. If it doesn't, this is a **Decision Required** item for the project
   owner — not something settled by majority vote among agents.

## Requirements Traceability

This project doesn't need a separate requirements-tracking tool yet — one
owner, one repo, no ticketing system. Traceability lives in:

```
Requirement (from the project owner)
    → app-workflow.md entry (the flow it produces)
    → tests/ (the tests proving it)
    → solutions.md (if a significant decision was involved)
```

The Orchestrator must be able to point to the test(s) that prove a given
requirement works. If a requirement has no corresponding test, that's a
gap to surface, not silently accept.

## Definition of Done

A feature is done when, in addition to `testing-workflow.md`'s
tests/lint/type-check gate:

- The coverage matrix for the change has no unresolved "Requires
  investigation" or "Requires human decision" rows.
- `app-workflow.md` reflects the new flow (if behaviour changed).
- `solutions.md` has an entry (if a significant decision was made).
- Regression risk has been explicitly considered, not just "tests pass."
- Any Level 3+ change has had a post-implementation review pass.

## TDD Integration

`testing-agent` participates during the **analysis** phase, before any code
exists — its job is to shape the test strategy (normal/edge/invalid/failure
categorisation per `testing-workflow.md`), not to review tests after the
fact. The actual RED→GREEN→REFACTOR cycle remains the Orchestrator's,
per "Implementation" above.

## Post-Implementation Review

For Level 3+ changes, after implementation, re-invoke the specialists whose
concerns are most likely to be affected by integration (usually
`architecture-agent`, `testing-agent`, and — if the change was
security/performance-relevant during analysis — those two again) to check
for problems introduced during implementation that the design-phase review
couldn't see. Level 4 additionally gets `production-readiness-agent`.

## Regression Awareness

No new process here — `rules.md` and `testing-workflow.md` already govern
this ("what existing behaviour could this change break"). The Orchestrator
folds this question into the coverage assessment rather than treating it as
a separate gate.

## Decision Documentation

Significant multi-agent decisions (agent roster changes, review-level
recalibration, a conflict that required human resolution) get an entry in
`solutions.md`, following the existing entry format (Problem / Context /
Requirements / Constraints / Analysis / Decision / Reasoning / Trade-offs /
Result / Future Considerations). No new decision-record file — `solutions.md`
already serves this purpose project-wide.

## Git Workflow Integration

Multi-agent analysis happens **before** a feature branch is created — it's
part of "Analysis / Plan" in `coding-workflow.md`'s full cycle, not a
parallel process. Nothing here changes branching, commit, or PR conventions.

## Human Approval Boundaries

No new boundaries beyond `rules.md` "Safety" and "Changes." Two multi-agent-
specific additions:

- Adding a new orchestration layer (sub-orchestrators) requires the
  documented justification in "Why No Additional Orchestration Layer Now"
  to be updated and presented, not silently introduced.
- Changing the specialist roster (adding/removing an agent file) is a
  process change and should be mentioned to the project owner, though it
  doesn't rise to the level of the destructive/architectural items in
  `rules.md` that require a stop-and-ask.

## Limitations and Risks of This Architecture

- **Coordination overhead for small changes.** Running a coverage
  assessment for a one-line fix is wasted ceremony — mitigated by Level 1
  explicitly skipping it.
- **Specialist blind spots from narrow framing.** A specialist only
  investigates what it's asked; a poorly scoped question produces a
  confidently narrow (not wrong, just incomplete) answer. Mitigated by the
  Agent Output Contract's `Questions` and `Confidence` fields surfacing
  when a specialist thinks its brief was too narrow.
- **No enforcement mechanism.** Nothing technically stops the Orchestrator
  from skipping the coverage assessment under time pressure — this is a
  process discipline, same category as the convention-only PR review
  already accepted in `rules.md`.
- **Read-only specialists can recommend contradictory fixes** that only
  surface as broken when the Orchestrator actually implements them serially.
  Mitigated by synthesis explicitly surfacing conflicts before
  implementation starts, not after.
- **Single point of synthesis failure.** All specialist findings pass
  through one Orchestrator's judgment; there's no independent check on the
  synthesis itself except the post-implementation review pass (Level 3+
  only). Level 1–2 changes have no check on synthesis quality beyond normal
  PR review.

## Why No Additional Orchestration Layer Now

Per the project's own instruction, this requires explicit justification —
absence of justification is not sufficient reason to add one.

- **Current Orchestrator is not insufficient.** There is exactly one
  project owner, one repository, and (as of this writing) zero business
  logic. A single Orchestrator can hold full context for every change.
- **No complexity is causing a problem.** Sub-orchestrators solve
  *coordination* problems that appear when there are enough parallel
  workstreams that one orchestrator can't hold all the dependency edges in
  its head, or when domains (e.g. "domain rules" vs. "infrastructure") are
  genuinely separate teams. Neither is true here.
- **No responsibility exists that a new layer would own.** The three
  candidate layers (Domain, Technical, Operations) would each currently
  have almost nothing to do — there's no domain logic, one technical
  surface (a CLI), and no deployed operations.
- **Added complexity would exceed the benefit.** An extra layer adds
  hand-off overhead, more places for a decision to get lost between layers,
  and more documentation to keep in sync — for zero coordination problem
  it would actually solve today.

**Re-evaluate this when:** the project has multiple genuinely independent
domain areas in flight concurrently, a second human collaborator joins and
needs their own delegation path, or the specialist roster grows large
enough that the Orchestrator itself can't hold the dependency graph between
them for a single requirement.

## Confirmed Decisions (resolved 2026-09-06)

These were raised as open questions and confirmed as-is by the project
owner without modification:

1. **Specialist roster tool access.** Specialists remain read-only by
   design (see "Roles"). Revisit only if this becomes a genuine bottleneck
   in practice — not a scheduled reconsideration.
2. **`devops-agent` and `production-readiness-agent` stay dormant** until
   CI/CD or a deployed system respectively becomes real. Their near-empty
   findings until then are expected, not a signal something's wrong.
3. **Devil's Advocate stays a dynamic brief**, not a dedicated agent file —
   applied to whichever existing specialist is least invested in the
   original recommendation, per requirement.
