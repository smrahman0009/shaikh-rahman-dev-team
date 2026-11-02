# Ledger operations

Requires Python 3.11+. Resolve the toolkit path and explicit target project path; run help first if the installed version differs. Commands below are actual toolkit commands, not Codex slash commands.

```text
python <toolkit>/team.py --project <target> init --brief <original-brief> --config <config.json>
python <toolkit>/team.py --project <target> status
python <toolkit>/team.py --project <target> request --file <action.json>
python <toolkit>/team.py --project <target> check --id <task-id> --actor <critic-thread-id> --token <review-token> --argv <check-command.json>
python <toolkit>/team.py --project <target> export
```

`--config` is optional. Workflow modes map to config `mode`: `collaborative`, `autonomous`, `research`. No API key is required by the ledger. Actual agents are executed by the Codex session. The ledger does not start, stop, sandbox, or authenticate them.

## Assignment sequence

1. Create tasks using JSON `action: task`, with `actor`, `id`, `purpose`, `approach`, `owner_role`, `critic_role`, `profile`, `stage`, nonempty `acceptance`, explicit relative `files`, and `depends_on`. Stages are requirements, design, planning, implementation, or validation. Dependencies must already exist.
2. Dispatch a bounded native producer. It claims the task with `action: claim`, its actual thread ID as `actor`, and the task `id`. Preserve the returned token. Successful claim, not a prompt alone, grants ledger ownership.
3. The producer edits only assigned artifacts and submits with `action: submit`, matching `actor`, `id`, `token`, and a concise outcome `summary`. Submit fingerprints the task artifacts.
4. Start a fresh native critic. It uses `action: review_start`, its actual thread ID, and the task ID. The returned `packet` intentionally excludes the producer's approach, summary, reviews, and conversation. Pass only that neutral packet and role/verification instructions for the initial assessment. Preserve the separate review token.
5. The critic performs verification through `check` using a JSON array of command arguments, or records justified document inspection with `action: inspection`, matching identity/token, a summary, and existing relative evidence-file paths. Inspection is not a substitute for executable checks when execution is needed to establish behavior.
6. The critic submits `action: review`, matching identity/token, `verdict: approve` or `revise`, `summary`, and a `findings` array. Each finding has `id`, `severity` (blocking, major, minor), `evidence`, `impact`, and `verification`. Approve needs current passing evidence and no unresolved material findings.
7. For `needs_revision`, the producer claims again, addresses supported findings, and resubmits. Keep the discussion in the task history; the initial review remains independently recorded. Exhausted rounds require explicit escalation, not a new task ID to evade the limit.

Native actor identities and independent contexts remain the coordinator's responsibility. Tokens reject stale or foreign results within the ledger; they are not an authentication system against a malicious caller.

## Controls and records

- `pause` / `stop`: record the state, revoke assignments; also interrupt actual native workers.
- `recover`: use only after previous workers have stopped; set `workers_stopped: true` truthfully. Reconcile returned stale artifacts before redispatch.
- `change`: after an authorized requirement update and worker shutdown, supply reason and `workers_stopped: true`. Replan affected work; never rewrite the CEO's intent merely to pass checks.
- `block`: record an actionable reason and escalate.
- `mode` / `budget`: change only within existing authority and with a recorded reason. Budget exhaustion does not authorize increasing one's own allowance.
- `decision`: record question, choice, reason, alternatives, and dated sources.
- `reserve`: reserve research or experiment capacity before performing that work. Counters only enforce work registered through the tool.
- `usage`: record attributable measured USD or null, with source; missing platform billing remains unknown.
- `lesson_propose`, `lesson_review`, `lesson_retire`: maintain reviewed, scoped knowledge. Read learning.md before promotion.
- `deliver`: all tasks must be accepted, an independently reviewed validation task must exist, and the handoff must be among reviewed artifacts. The CTO should first request the auditor for consequential claims.

Use the toolkit examples and implementation for exact request shapes beyond the assignment sequence. `export` creates a human-readable history in the project's `.startup-team` directory. This history includes producer decisions and review events; do not feed it wholesale into a critic's initial context.

## Boundaries

The ledger gates declared file ownership, accepted dependencies, hashes, task transitions, review identity separation, revision counts, activations, registered research/experiments, verification commands, and deadline checks. Those controls apply only to work routed through it. Native agents can still consume tokens or write outside declared ownership unless platform permissions and orchestration prevent it. Documentation review is evidence-backed human/agent judgment, not automatic semantic proof. File hashes detect changes, not correctness. No automatic restart service or monetary spending cap is implied.
