# SR Dev Team

A portfolio project by **Shaikh Rahman**, software developer and data scientist.

A reusable agentic delivery toolkit for software, data engineering, analytics and ML projects. I designed the startup-style workflow around specialist roles, independent producer-critic reviews, and evidence-based delivery, and built the implementation with Codex.

## What this project demonstrates

- Task decomposition and coordination across CTO, product, architecture, development, ML and QA roles.
- Independent reviews using fresh agent contexts and neutral review packets.
- A Python/SQLite ledger with persistent limits, dependency tracking, stale-result rejection and recovery.
- Reviewed, scoped lessons that can transfer between projects without copying private runtime data.
- Automated tests and documented live-agent demonstrations, including detection of an ML evaluation leak.

For software engineering or data science opportunities, connect through [my GitHub profile](https://github.com/smrahman0009).

Invoke **SR Dev Team** with `$sr-dev-team`.

A reusable Codex workflow: CEO intent → CTO routing → appropriately scoped specialists → independent critics → verified delivery. Supports application, data engineering, analytics and ML work.

The original [implementation prompt](docs/prompt-original.md), [expert critique](docs/prompt-critique.md), and [revised brief](docs/implementation-brief.md) are saved separately from your future projects' requirements.

New to Codex skills? Read [skills explained in plain language](docs/skills-explained.md).

Previously installed `$startup-team`? See the [name migration note](docs/name-migration.md).

## Start in VS Code

Requirements: Python **3.11+**, a signed-in Codex client supporting skills and native subagents, and normal project execution permissions. The toolkit itself uses only Python's standard library; no API key or paid dependency is required by its scripts. Agent work consumes your existing Codex allowance.

1. Run the installer below to expose the skill in the target repository, or open this toolkit directory as your workspace.
2. Start a fresh Codex chat if the skill/agents do not appear. Type `$` and select `sr-dev-team` (or use `/skills` when available).
3. Provide your business requirements and target project. Invoke:

```text
$sr-dev-team
Use this repository as the target project. Read business_requirement.md.
Use autonomous delivery mode. Start with the smallest useful milestone.
Use independent critics and explain tasks in plain language.
```

Opening the toolkit alone does not authorize building the sample projects. Name the actual target when it differs from the current workspace. Do not use this framework's implementation brief as a product requirement.

To install into an existing repository:

```powershell
python install.py --target PATH_TO_YOUR_PROJECT
```

Installation copies the portable toolkit to `tools/sr-dev-team` and registers its skill under `.agents/skills/sr-dev-team` and its prefixed roles under `.codex/agents`. It never overwrites differing files. A preflight lists conflicts before writing anything; `--check` reports the plan only. Your Codex environment may require permission for these configuration directories. No global settings are changed.

## Talk to the CTO

Ask normally: “Show status and blockers”, “Explain the architect's choice”, “Prioritize the API”, “Review this assumption independently”, “Pause all agents”, “Resume after checking current files”.

Modes are `collaborative`, `autonomous`, and `research`. Autonomous permits routine decisions within existing scope and authority. Research mode prevents ledger dispatch of implementation tasks. The CTO remains responsible for interpreting business decisions and respecting actual execution permissions.

Pause/stop has two parts: interrupt native worker threads using the host, then revoke their ledger assignments. Recovery requires confirming old workers have stopped. Late results with revoked tokens are rejected. No command here starts a background daemon or automatically resurrects a closed Codex session.

## Portable task ledger

The agent uses `team.py`; you normally interact through the skill. All commands require an explicit project root. A project owns its original `business_requirement.md`, normal source and delivery artifacts, and a private `.startup-team/state.sqlite3` ledger. Keep that runtime directory out of version control; publish deliberately selected delivery documents instead.

```powershell
python team.py --project PATH init --brief PATH_TO_BRIEF
python team.py --project PATH status
python team.py --project PATH request --file action.json
python team.py --project PATH export
```

Initialization copies brief bytes exactly and refuses to overwrite a different existing requirement. It does not modify your application. `export` produces `.startup-team/history.md` with task evolution and recorded decisions. SQLite transactions serialize updates. Treat ledger files as project data, not as an adversarial security boundary.

`status` is deliberately compact to reduce repeated context. Use `status --full` only for detailed audit; do not send it to a critic before its initial independent assessment.

See [request examples](examples/requests/) and the skill's [ledger reference](.agents/skills/sr-dev-team/references/ledger.md). Requests are JSON files, avoiding shell quoting of prompts, scripts or dollar signs. Agent `actor` values should be actual host thread IDs. Tokens and hashes reject stale assignments; caller identity is not cryptographically authenticated.

Typical sequence: `task → claim → submit → review_start → check/inspection → review → deliver`. Each claim returns its token. Use a fresh-context critic, who obtains the neutral packet returned by `review_start`. The packet omits the producer's approach, summary and previous discussion. The critic may read original requirements and artifacts; logs and producer rationale stay out of its initial input.

Checks execute an explicitly authorized argument array with `shell=False`:

```powershell
python team.py --project PATH check --id TASK --actor CRITIC_ID --token TOKEN --argv check-command.json
```

Example argument file: `["python", "-B", "-m", "unittest", "discover", "-s", "tests"]`.

Checks are real local commands subject to the host's permissions. They are not additionally sandboxed by Python. Do not allow unchecked generated command requests to cross an authorization boundary. A timeout terminates the direct subprocess; descendant-process management remains the host's responsibility. Capture output may contain project-sensitive information; keep runtime state local.

Document stages may use an evidence-backed `inspection`; code and ML behavior should use executable checks as appropriate. The ledger verifies evidence presence/freshness and exit codes, not whether the chosen tests are sufficient. A separate validation task and reviewed handoff are required for delivery.

Every recorded check in a submission must pass. If a verification command itself was malformed, explain that infrastructure issue and use a bounded resubmission with corrected checks; do not silently erase the failure. Earlier review cycles and check events remain recorded. Saving verification code to a script and passing its path avoids complex command quoting.

Declare all output artifacts, including relevant tests, in task `files`. Reserve nonoverlapping ownership while writers/reviewers run. Hashes describe the current accepted artifact version; if a later task changes an earlier accepted artifact, replan and re-review affected work rather than accepting stale claims. The initial implementation uses conservative invalidation on a requirement change (all tasks). It does not automatically infer minimal change impact.

## Limits and control boundaries

Pass a JSON configuration with `init --config FILE`; defaults:

| Setting | Default | What code enforces |
|---|---:|---|
| `mode` | `collaborative` | Valid modes; research blocks implementation dispatch |
| `max_active` | 2 | Registered producers and critics concurrently assigned |
| `max_claims` | 40 | Total agent assignments, including retries/reviews |
| `max_revisions` | 2 | Maximum repairs and three total producer claims per task |
| `max_check_seconds` | 120 | Direct verification subprocess timeout |
| `max_checks` | 60 | Registered verification attempts |
| `max_research` | 8 | Research reservations |
| `max_experiments` | 8 | Experiment reservations |
| `deadline_seconds` | 14400 | Elapsed deadline checked before controlled progression |

Limits persist across recovery. Replacing a task does not erase its producer-attempt budget. Interrupted attempts also count. Changing limits requires an explicit `budget` request with a reason and existing user authority; the tool cannot authenticate that authority. Creating a new task to bypass a limit violates the skill protocol.

Platform-enforced: execution permissions and actual native context/thread capabilities.

Code-enforced when using the ledger: transitions, dependencies, matching tokens, actor separation, persistent counters, declared ownership, fingerprints, pending-check gates, evidence presence, and transactional updates.

Instruction-only: semantic quality, true agent identity, fresh-context discipline, appropriate model selection, research relevance, CTO routing, and worker adherence to file ownership. A role's instruction to avoid editing is not an OS read-only sandbox.

No monetary hard cap is claimed: complete provider billing is unavailable. `usage` records measured USD or null and its source; reports explicitly mark partial/unknown coverage. Configured operational budgets do not prevent a native agent from spending tokens outside registered work.

Record observed outcomes with `feedback`: `task`, boolean `accepted`, actual `human_minutes`, boolean `repeat_mistake`, and `source`. Status reports acceptance using the latest explicit feedback per task and requirement revision, total reported human review minutes, reported repeat mistakes, and repair rounds. Without feedback these outcomes are unknown. Cost per accepted task remains unknown without complete billing coverage.

## Learning and model selection

`lesson_propose` requires problem, cause, correction, applicability, evidence, prevention and scope. A different reviewer approves or rejects it. Identical normalized problem/correction pairs are deduplicated. Retire superseded or contradicted lessons with reasons; propose replacements under new IDs. Semantic contradiction detection is reviewer work, not an automatic theorem checker.

```powershell
python team.py --project PATH knowledge --scope specialist --query "leakage evaluation"
python team.py --project PATH knowledge-export --output reviewed-lessons.json
python team.py --project OTHER knowledge-import --file reviewed-lessons.json --actor CTO_ID
```

Retrieval is simple keyword filtering of approved local lessons. Cross-project export includes only non-project lessons explicitly marked `transfer_safe: true` by an independent reviewer; source evidence and project identifiers are omitted. The reviewer must actually check the remaining content for sensitive specifics. Imports become proposals and need fresh local approval. Nothing is automatically copied to a global memory store.

Models inherit the current session default. Choose available models/effort through supported host controls or role configuration only after checking availability. Do not assume that a cheaper model saves total cost, or invent current pricing. The CTO compares substantial options against dated primary sources and records the decision; it retrieves only applicable knowledge/profile sections.

## Verification

```powershell
python -B -m unittest discover -s tests -v
python -B validate_bundle.py
```

The tests execute ledger transitions, real verification subprocesses, races, interruption, budget failures, stale artifacts, ML leakage fixtures, and knowledge transfer. They do not simulate model intelligence as proof of real agent independence. See [validation report](docs/validation.md) for live-agent evidence and environment limitations.

Official interfaces verified on 2026-11-02: [skills](https://learn.chatgpt.com/docs/build-skills), [custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [permissions](https://learn.chatgpt.com/docs/permission-modes). Local CLI inspected: `0.164.0-alpha.11.1`. Native capabilities may vary by client; the skill discloses generic-role fallback if custom roles are not loaded.
