# Startup delivery team: implementation brief

## Objective and scope

Build a reusable, evidence-led engineering team for application development, data engineering, analytics, and ML. The user acts as CEO; a CTO is the primary contact and selects the smallest useful set of specialists. Optimize accepted results and total effort, including repair and review. Do not assume that more agents improve outcomes.

Keep the framework under `tools/sr-dev-team`, with only documented native integration files outside it. Preserve this repository's Next application and unrelated work. The original request is preserved byte-for-byte in [prompt-original.md](prompt-original.md); this brief operationalizes it and does not replace project business intent.

Use native Codex skills and supported agent configuration after checking official documentation and the installed environment. Implement durable bookkeeping and validation with Python's standard library when available. Provide setup instructions if prerequisites are absent; do not install runtimes automatically, assume API credentials, or introduce a paid service. A supported skill entry point must be real and discoverable; document how a fresh session loads it. Do not invent native commands.

## Authority and enforcement

Document each meaningful guarantee with one of these labels:

- **Platform-enforced:** actual sandbox, tool authorization, available agent/model capabilities, and platform context isolation. Configuration cannot grant permissions beyond the host.
- **Code-enforced:** validations performed when using the ledger, including permitted state transitions, persisted counters, stale-result checks, evidence requirements, and durable updates. Tests must exercise rejection paths. File access outside the ledger remains possible; this is not a tamper-proof security system.
- **Instruction-only:** CTO routing, research judgment, semantic correctness, critique quality, appropriate delegation, and relevant knowledge selection where not mechanically checked. Record evidence rather than treating compliance as automatic.

The initial deliverable is an interactive instruction-driven team with durable state and recovery procedures. Do not imply an unattended daemon exists. Ledger cancellation does not itself terminate an already executing host tool or agent; the CTO must stop live work through actual host controls. If a runner is not implemented and tested, unattended scheduling and automatic restart remain explicit gaps.

## Intake, team, and workflow

Each project has its own team directory with `business_requirement.md` as authoritative intent. Preserve English, Bangla, and mixed-language wording. Store structured requirements separately with source references, confirmed requirements, assumptions, unresolved questions, project domain, acceptance criteria, and revision provenance.

Provide permanent definitions for CTO, product/business analysis, architecture, software development, data engineering, data science/ML, QA, and technical audit, plus independent critique instructions appropriate to each role. Compose permanent role, project expertise profile, and task contract. Activate or combine roles proportionately; use the actual platform concurrency ceiling.

Follow intake → requirements → design → task planning → implementation → independent review → integrated validation → delivery. Sequentialize dependencies. Parallel work requires isolated worktrees or explicit nonoverlapping file ownership. Small tasks may combine stages and receive one concise independent review; substantive requirements, consequential design, implementation, and final delivery claims still require meaningful critique.

Route code defects to developers, design defects to architects, and ambiguous expected behavior to product analysis. The technical auditor reviews consequential CTO decisions and final claims. Verification evidence outweighs consensus.

## Task and critique contracts

Record ID, owner, status, dependencies, scope, plain-language purpose, expected result, acceptance criteria, relevant files/interfaces, constraints, proposed approach, material alternatives when useful, decisions, changes, findings, resolutions, verification, limitations, and next action. Keep small notes short and link larger milestones. Preserve explainable decisions, not private chain-of-thought or every tool invocation.

A critic receives a fresh context containing original intent, acceptance criteria, current artifacts, and pertinent evidence. Do not include the producer's full conversation. Record an initial assessment before exposing producer rationale or self-review. Critics may inspect source and run independent checks; findings identify evidence, impact, and verification method. Approval without objections is valid. Producers own revisions; critics do not race to edit their artifacts.

Every finding needs resolution or explicit justified disposition. Default to at most two revision rounds per stage, configurable and persisted. Material unresolved disagreements become blocked/escalated CTO decisions; missing or contradictory business intent goes to the CEO when required. Changing a model is optional and does not guarantee independence.

## Autonomy, decisions, and controls

Support collaborative, autonomous delivery, and research-and-propose modes. In collaborative mode consult on material decisions; in autonomous mode decide reversible details within scope, authority, and limits; in research-and-propose mode stop after a reviewed plan. Support natural-language status, explanations, changes, reprioritization, specialist review, pause, resume, and stop through the CTO. Execution permissions remain separate from decision autonomy.

Inspect the existing stack before consequential technology decisions. Compare a few suitable options using current official compatibility, support, and pricing information where relevant. Record dated sources, project fit, implementation/operating effort, reliability, maintenance, reversibility, assumptions, and a research freshness policy. Discover models from the actual platform when exposed; otherwise record the discovery limitation and inherit a supported default. Never fabricate prices or billing usage.

Provide configurable concurrency, revision, runtime, research, experiment, and measurable spend limits. State exactly which operations each local limit controls. Persist bounded retries and loop counters across restart. Check controlled budgets before starting further controlled work. A cooperative runtime check cannot interrupt a hung external command or enforce provider billing. Unknown usage remains unknown.

## Durability, change, and learning

Use transactional/atomic state changes and validated transitions. Checkpoint tasks and record clear blocked outcomes. Resume reconciles recorded work with actual repository/artifact state; saved “in progress” does not establish a live worker. Record requirement changes and impact, invalidate affected approvals and downstream work, and reject results with stale provenance. Checkpointing preserves evidence and pending work; it is not background execution.

Store reviewed knowledge at user-preference, team, specialist, project, and temporary-task scopes. A proposed lesson includes problem, cause, correction, applicability, evidence, and prevention. Critique before promotion; support relevant retrieval, deduplication, revision, retirement, and explicit contradiction handling. Keep sensitive or project-specific details out of unrelated contexts. Convert recurring lessons into checks where practical. This is persisted knowledge and workflow improvement, not model-weight retraining.

Report acceptance rate, repeat mistakes, human review time, repair rounds, and cost per accepted task when sufficient data exists. Define denominators, distinguish observed from supplied data, and show unknown or insufficient-data outcomes honestly.

## Validation and delivery criteria

Verify the following with repeatable tests or documented demonstrations:

1. A software task with a seeded defect yields an independent finding, producer repair, and meaningful verification.
2. An ML task with leakage or invalid evaluation is rejected; review checks baselines, reproducibility, evaluation integrity, and training/inference consistency. A valid negative result is acceptable.
3. A requirement change invalidates affected approvals and rejects a stale result.
4. An interrupted run resumes from durable state only after reconciliation with actual artifacts.
5. Producer–critic disagreement reaches a justified disposition or bounded blocked/escalated outcome.
6. Budget exhaustion blocks further controlled progression and retries remain bounded across restart.
7. A trivial task avoids activating the whole team and receives brief independent review.

Also check illegal transitions, missing evidence, concurrent update handling where supported, knowledge promotion and scope, and setup portability. Label simulations, ledger unit tests, and real host multi-agent demonstrations separately. A synthetic record of a critic is not evidence that a separate context ran. Preserve concise, inspectable results and avoid unrelated application test changes.

Deliver reusable definitions, supported entry point/launcher, setup and operation guidance, configuration reference, example requirements and sample projects, task/decision/critique/knowledge/handoff templates, verification results, usage information, and known limitations. Explain inspection, pause, resume, stop, extension, prerequisites, and installation scope. End with a concise account of what works, how to invoke it, what was verified, and any capability gaps.
