# Codex skills, in plain language

A **skill** is a reusable working procedure that Codex can read when a task needs it. It can contain instructions, supporting references, examples and executable helpers.

**Skill Creator** is a built-in assistant for creating or improving these folders. It helps write the skill; you do not need to run Skill Creator every time you use the finished skill.

For this project, Skill Creator guidance helped build `startup-team`. You run the finished workflow by mentioning `$startup-team` in a Codex chat.

## What the files mean

```text
.agents/skills/startup-team/
  SKILL.md                 When to use the workflow and how to coordinate it
  references/              Detailed rules loaded when needed
  agents/openai.yaml       Display name and suggested invocation in the UI

.codex/agents/
  startup_cto.toml          CTO role instructions
  startup_developer.toml    Software developer role instructions
  startup_ml_engineer.toml  ML specialist role instructions
  startup_*_critic.toml     Independent review role instructions

team.py                    Durable task, review, budget and knowledge ledger
```

The `agents/openai.yaml` file describes the skill's UI. The separate `.codex/agents/*.toml` files define the team's specialist roles.

## How a skill is formed

Every skill needs a `SKILL.md` file. Its first section names the skill and describes when it applies:

```yaml
---
name: startup-team
description: Coordinate specialist agents to deliver reviewed project work.
---
```

Below that section are the instructions Codex follows. Additional files are included only when they help the workflow.

## What happens when you use this one

1. You write your project intent in `business_requirement.md` and invoke `$startup-team`.
2. Codex reads the skill and acts as your CTO.
3. The CTO selects suitable specialists and creates bounded tasks.
4. Native subagents do the work and independently critique it.
5. `team.py` saves task state, checks transitions and rejects stale approvals.
6. The CTO returns the deliverable, verification results and remaining limitations.

The skill is the playbook. The native agents execute it. The Python ledger tracks and checks registered work. They serve different purposes.

Skills load progressively: Codex first sees the name and description, then reads the full instructions when selected. Supporting references are read when relevant. This helps keep unnecessary context out of routine work.

## How to invoke it

Open the project in VS Code and start a Codex chat:

```text
$startup-team
Read business_requirement.md.
Use autonomous delivery mode.
Start with the smallest useful milestone.
```

You can also type `$` to select an available skill or use `/skills` where supported. If a newly installed skill does not appear, start a fresh session or reload the client.

The skill does not train a new model or create an always-running service. It gives the existing model a reusable workflow. Saved knowledge and task records help future sessions resume and reuse reviewed lessons.

Official references: [Build skills](https://learn.chatgpt.com/docs/build-skills), [Subagents and custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
