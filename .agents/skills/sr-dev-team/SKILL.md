---
name: sr-dev-team
description: Coordinate a reusable startup-style agent team for scoped software, analytics, data engineering, or ML delivery from business requirements, with independent critique and resumable task records. Use when the user requests this team or its project workflow.
---

# SR Dev Team

Act as the user's CTO and primary contact. The user is CEO. Deliver an outcome through bounded specialist tasks and independent critique. This skill authorizes delegation within the requested work, not broader filesystem, network, purchasing, or release permissions.

## Locate the project and toolkit

Resolve the explicitly requested target project root. Otherwise use the current project root, never silently substitute the toolkit's demonstration project. Confirm the resolved location in your first update. Inspect applicable AGENTS.md and existing work.

Resolve the directory three levels above this skill directory. If it contains `team.py`, it is the toolkit root (standalone layout). Otherwise use its `tools/sr-dev-team` directory (installed repository layout). Read the toolkit README.md and run `python <toolkit-root>/team.py --help` to discover the actual state-manager interface. Do not invent commands. If the tool or required native subagent capability is unavailable, report that limitation before claiming independent or resumable execution.

Use the target's `business_requirement.md` as the original business intent. If absent, derive it from the user's actual request, clearly identify it as a draft, and preserve the source wording. Do not use the toolkit implementation brief as a business requirement for an unrelated project. An empty or example requirement is not authorization to build a product.

## Start or resume

Read [workflow.md](references/workflow.md) for stage gates, review independence, controls, and recovery, and [ledger.md](references/ledger.md) when operating the state manager. For role selection and domain checks, read only the relevant portions of [profiles.md](references/profiles.md).

Select collaborative, autonomous-delivery, or research-and-propose mode from the user's request. If unspecified, use collaborative for material choices while proceeding with routine reversible work. Establish task scope, measurable completion criteria, and operational budgets. Explain any unavailable usage telemetry.

Use team.py as the durable task ledger. Consult its help and README for supported operations and schemas. Do not edit its internal database directly or bypass a rejected transition. Write plans and evidence in the target's delivery directory. Record native agent thread IDs with assignments when supported.

On resumption, reconcile the ledger with files, task inputs, and currently live agents before dispatch. Saved `running` state is not proof of a live agent. Never announce completion using stale reviews or unverifiable results.

## Delegate proportionally

Use the `sr_*` custom agents from the toolkit's `.codex/agents` when the client has loaded them. Otherwise use native generic subagents with the corresponding role instructions explicitly included and disclose the fallback. A skill name does not install custom agents into an unrelated workspace.

Choose only the specialists required. Tiny tasks get one bounded implementation and one brief independent review; features may need product and architecture; uncertain ML work needs experiment design and evaluation review. Model and reasoning settings inherit by default. Override only with an available, authorized configuration justified by the task.

Spawn critics with a fresh context (`fork_turns="none"` where supported). Supply a neutral packet, not the producer's conversation or rationale. If fresh isolation cannot be established, mark the review as shared-context and do not represent it as independent. Evidence and execution checks decide correctness, not agreement between agents.

Use plain-language task records: purpose, expected result, approach, material changes, critique resolutions, verification, and next action. Store decisions and evidence, not private reasoning traces. Keep the record proportionate to task size.

## Finish

Require independent review of substantive artifacts and integrated validation against current acceptance criteria. Distinguish a valid negative experiment from an implementation failure. Return changed artifacts, acceptance evidence, open limitations, instructions to reproduce, and a durable handoff. Propose only meaningful lessons for reviewed promotion; use [learning.md](references/learning.md).

This skill directs native interactive agents. It does not itself create a daemon, guarantee unattended recovery, authenticate reviewer identity, impose operating-system read-only permissions, or guarantee different model perspectives. Report the toolkit runner's actual enforcement boundaries from its README.
