Build a reusable, production-minded agentic delivery team for software engineering, data engineering, analytics, and machine learning projects.

Act as the implementation lead. Inspect the environment, verify current platform capabilities using official documentation, design the system, implement it, and validate it. Deliver working artifacts rather than stopping at a proposal.

MISSION

Create a small-startup-style organization that turns my plain-language business requirements into reviewed, verified deliverables with minimal supervision.

I act as CEO. A CTO agent coordinates the team and serves as my primary contact. Specialists perform the work, and independent critique partners review their outputs.

Optimize for reliable accepted results, low human supervision, and low total cost—including retries and review. Do not promise perfection or assume that additional agents automatically improve quality.

1. PROJECT INTAKE

Use business_requirement.md at the root of each project’s team directory as the authoritative record of my business intent.

Accept informal English, Bangla, or mixed-language requirements.

Preserve my original wording. Generate structured requirements separately, with links back to the source statements. Distinguish confirmed requirements, assumptions, and unresolved questions.

Detect whether the project involves application development, data engineering, analytics, ML, or a combination. Select specialist profiles accordingly.

Support small tasks and large projects. Scale planning, documentation, and active agents to the work.

2. TEAM ORGANIZATION

Implement these roles and their critique partners:

- CTO / Delivery Coordinator: route requests, manage dependencies, budgets, project state, escalations, integration, and delivery.
- Product Manager / Business Analyst: define scope, user stories, priorities, and measurable acceptance criteria.
- Software Architect / Tech Lead: design interfaces, components, data flow, and bounded implementation tasks.
- Software Developer: implement application functionality and relevant tests.
- Data Engineer: implement ingestion, transformations, schemas, and data-quality checks.
- Data Scientist / ML Engineer: design and implement experiments, training, evaluation, and inference.
- QA / Validation Engineer: independently verify integrated behavior and acceptance criteria.
- Technical Auditor: review consequential CTO decisions and final delivery claims.

Roles may be combined or activated selectively. Do not spawn the entire organization for every request. Every substantive stage output must receive independent critique; trivial-task reviews should remain brief.

Define agents through three instruction layers:
permanent role + project expertise profile + specific task contract.

3. INDEPENDENT PRODUCER–CRITIC REVIEW

Treat independence as a workflow requirement, not a personality label.

- Run the critic in a separate context.
- Give it original requirements, acceptance criteria, the artifact, and relevant evidence.
- Have it perform an initial assessment before reading the producer’s rationale or self-review.
- Let it independently inspect source files and run checks.
- Do not forward the producer’s full conversation by default.
- Ask it to find counterexamples, missing cases, invalid assumptions, and failure modes.
- Require findings to include evidence, impact, and a verification method.
- Permit approval without invented objections.
- Keep the producer responsible for revisions; avoid simultaneous edits to the same artifact.
- Track each finding through resolution or an explicit, justified disposition.
- Use different models selectively when available and useful; do not claim this guarantees independence.
- Make verification evidence more authoritative than agent consensus.

Start with at most two revision rounds per stage, configurable by project. Escalate material unresolved disagreements to the CTO, and unresolved business-intent questions to me when required by the selected autonomy mode.

4. WORKFLOW AND ROUTING

Implement:
intake → requirements → design → task planning → implementation → independent review → integrated validation → delivery.

Allow stages to be shortened or combined for small tasks while preserving meaningful review.

Run dependent stages sequentially. Parallelize independent work using separate worktrees or explicit file ownership.

Route failures to their actual source:
implementation defects to developers, design defects to architects, ambiguous expected behavior to product management.

When I change direction, record the change, assess its impact, invalidate affected approvals or tasks, and update dependent work.

Support cancellation, checkpointing, resumption, and detection of stale task results.

5. TASK CONTRACTS AND EXPLAINABLE HISTORY

For each task, record:
- ID, owner, status, dependencies, and scope.
- Purpose in easy language.
- Expected result and acceptance criteria.
- Proposed approach and meaningful alternatives where warranted.
- Subtasks when useful.
- Relevant files, interfaces, and constraints.
- Material decisions and changes, with supporting evidence.
- Critique findings and resolutions.
- Verification results, limitations, and next action.

Document how the task evolved without storing private chain-of-thought or every tool call.

Small fixes need short notes. Features need structured task briefs. Large projects need linked milestones and design records.

Critics must check that documentation matches the implementation, distinguishes plans from completed work, and is understandable to a newcomer.

6. CEO INTERACTION AND AUTONOMY

Provide one primary interaction channel through the CTO. Support natural-language requests for status, explanations, reprioritization, changes, specialist review, pause, resume, and stop.

Offer configurable workflow modes:
- Collaborative: consult me on material decisions.
- Autonomous delivery: make reasonable decisions within my stated scope, constraints, authority, and budget.
- Research and propose: investigate and deliver a reviewed plan before implementation.

In autonomous mode, avoid asking about routine implementation choices. Record assumptions and decisions. Escalate when authority, essential information, contradictory requirements, or budget constraints prevent responsible progress.

Separate decision autonomy from execution permissions. Respect the actual sandbox, platform policies, and my authorization. Never bypass permission controls.

7. CURRENT, COST-EFFICIENT DECISIONS

For consequential technology choices:
- Inspect the existing stack first.
- Research current official documentation, compatibility, support status, and pricing where relevant.
- Compare a small number of suitable options.
- Evaluate project fit, implementation effort, operating cost, maintenance, reliability, and reversibility.
- Record dated sources, assumptions, and selection rationale.

Prefer suitable, maintainable solutions over novelty. Reuse verified research with an appropriate freshness policy.

Select models and reasoning effort by task difficulty. Discover available models instead of hardcoding model names or prices.

8. SHARED LEARNING

Implement durable, reviewed knowledge at these scopes:
user preferences, team-wide practices, specialist lessons, project decisions, and temporary task state.

For meaningful failures or corrections, propose a lesson containing:
problem, cause, corrective action, applicability, evidence, and prevention method.

Have a critic validate accuracy and scope before promoting it to reusable knowledge.

Retrieve only relevant lessons. Support revision, retirement, contradiction handling, and deduplication. Prevent project-specific choices or sensitive information from leaking into unrelated projects.

Convert recurring lessons into automated checks where practical.

Describe this honestly as persisted knowledge and workflow improvement, not automatic retraining of model weights.

9. RELIABILITY AND EFFICIENCY

Implement configurable limits for concurrency, revisions, runtime, research, experiments, and spending where measurable.

Maintain durable task state with validated transitions, bounded retries, loop detection, and clear blocked states.

On resumption, reconcile saved state with actual repository changes. Do not assume that a previous “in progress” task is still running.

Use concise handoffs and relevant artifacts rather than replaying complete histories. Keep permanent instructions short and load specialist references on demand.

Measure:
acceptance rate, repeat mistakes, human review time, repair rounds, and cost per accepted task. Mark unavailable cost data as unknown rather than inventing it.

10. VALIDATION AND DELIVERY

Use meaningful verification for the orchestration, including:
- A software task with an intentionally seeded defect.
- An ML task involving leakage or invalid evaluation.
- A requirement change during execution.
- Interrupted-run recovery.
- Producer–critic disagreement.
- Budget exhaustion and bounded termination.
- A trivial task that should avoid excessive agent activation.

Mock orchestration logic where appropriate. Clearly distinguish simulated tests from real multi-agent execution.

For ML work, require evaluation integrity, baseline comparisons, reproducibility, and training/inference consistency. A valid negative experimental result is acceptable.

Final delivery must include:
- Working implementation and reusable agent definitions.
- A practical launcher or supported skill entry point.
- Setup, configuration, and operation instructions.
- Example business requirements and sample projects.
- Task, decision, critique, knowledge, and handoff templates.
- Verification results, known limitations, and available usage information.
- Instructions for inspecting, pausing, resuming, and extending the team.

IMPLEMENTATION RULES

First inspect existing files and applicable repository instructions. Preserve unrelated work. Choose a clear implementation directory and separate the reusable framework from any current application.

Verify current Codex agent, skill, configuration, and command support before choosing integration details. Do not invent native commands or imply that configuration files enforce behavior they cannot enforce.

Provide a convenient invocation such as $startup-team only if implemented as a real supported skill. Explain any installed prerequisites.

Distinguish an interactive instruction-based workflow from durable unattended execution. If unattended recovery requires a runner, implement and test that runner or explicitly identify the remaining capability gap.

Do not add a custom multi-agent framework or API dependency unless native capabilities cannot meet a concrete requirement. Do not assume API credentials or paid-service authorization.

Proceed autonomously on reversible work within scope. Ask only for essential missing information or required authorization. Finish with a concise report of what works, how to run it, what was verified, and what remains limited.