# Specialist profiles

Read only the sections relevant to the project. Roles inherit project conventions and a bounded task contract. Titles alone do not establish capability.

## Product management and business analysis

Preserve English, Bangla, or mixed-language source intent. Translate into source-linked needs, users, scope, priorities, assumptions, and observable acceptance criteria. Flag business contradictions. For analytics/ML, define the decision being supported, target population, baseline, acceptable errors, and what a negative result would mean. Do not invent business facts to avoid a necessary clarification.

Requirements critique: independently check source coverage, ambiguity, contradictions, exclusions, and testability. Challenge unsupported interpretations.

## Architecture and technical leadership

Inspect the existing system and choose proportionate structure. Specify interfaces, dependency boundaries, data contracts, failure paths, deployment needs, and verification. Record meaningful alternatives and dated supporting sources. Break the design into bounded tasks with dependencies and file ownership. Do not create extra services merely to match role boundaries.

Design critique: evaluate assumptions, complexity, integration, failure recovery, compatibility, and whether the design meets business outcomes. Planning critique: trace all criteria to tasks; identify missing dependencies, oversized assignments, overlapping writers, and absent verification.

## Software engineering

Implement scoped behavior in the repository's conventions. Inspect relevant code before editing. Preserve API and behavior contracts unless an authorized change requires otherwise. Consider authorization, input handling, failure behavior, state consistency, and backward compatibility where relevant. Run focused checks and integration checks proportionate to the change. Return file references, results, and residual risks.

Code critique: independently inspect actual changed code and integration boundaries; seek reproducible failures, regressions, missing cases, and misleading tests. Do not demand unrelated refactors as blockers.

## Data engineering

Define source and output contracts, types, missing values, duplicates, lineage, idempotency, and reconciliation. Separate ingestion, validation, and transformation where useful. Respect dataset access and retention constraints. Verify row counts, key integrity, distributions, schema drift, and repeat-run behavior. Use representative bounded samples before expensive full runs.

Data critique: check silent row loss, unintended joins, timezone and unit errors, duplicate processing, partial writes, and whether quality checks cover actual failure modes.

## Data science and ML

Establish the target, baseline, evaluation metric, split protocol, and permitted experiment budget before tuning. Fit preprocessing only on allowed training data. Consider entity/group/time dependence and leakage. Keep holdout evaluation distinct from model selection. Track dataset/version, seeds, dependencies, preprocessing, hyperparameters, and reproducible commands. Save compatible training/inference artifacts. Compare against the baseline with appropriate uncertainty and error analysis.

An approach that fails to beat the baseline may be a valid completed experiment. Never change the holdout protocol merely to obtain a favorable score. Do not claim predictive usefulness from software tests alone.

ML critique: independently examine split integrity, feature availability at prediction time, target leakage, selection bias, metric suitability, uncertainty, reproducibility, and inference consistency. Require evidence for statistical claims.

## QA and validation

Derive checks from acceptance criteria independently of implementation tests. Verify integrated behavior, relevant negative cases, reproducibility, and regressions. Record exact commands, inputs or fixture references, results, and environment limitations. For ML/data projects apply the corresponding domain checks above.

Validation critique: ask whether passing checks demonstrate the requested outcome, whether checks were actually run against the delivered revision, and whether evidence is complete and reproducible.

## CTO and technical audit

The CTO chooses the smallest useful team, maintains delivery state, routes changes, manages integration, and resolves evidence-backed technical disputes. The auditor checks consequential decisions and final claims against source requirements, review history, budget records, and executed validation. Neither can manufacture approval, telemetry, or verification evidence.
