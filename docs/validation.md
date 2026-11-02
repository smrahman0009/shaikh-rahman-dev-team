# Validation report — 2026-11-02

## Environment and scope

Windows PowerShell, Python 3.14.7, Codex CLI 0.164.0-alpha.11.1. The application code in this repository was not part of the change. Verification targets the toolkit, its portable installation, and small native-agent examples.

## Automated tests

Command: `python -B -m unittest discover -s tests -v`.

28 tests: **27 passed, 1 skipped**. The skipped test attempts a directory symlink escape during installation; this Windows account cannot create symlinks (WinError 1314). Ordinary traversal, artifact containment, conflict preflight, and no-overwrite behavior are tested. Do not interpret the skipped platform-specific test as a pass.

Coverage includes real subprocess verification of a seeded software defect and an ML subject-overlap fixture; transactional concurrent claims; producer/critic separation; pending-test approval races; deadlines and activation/check/research/experiment limits; persistent repair caps; interrupted assignments; changed requirements, dependencies and inspection evidence; reviewed knowledge promotion, transfer and local re-review; metrics; and portable/idempotent installation.

`python -B validate_bundle.py` passes for the skill frontmatter, reference links, toolkit entry point, and 15 TOML roles. The Skill Creator's generic quick_validate.py was unavailable because its PyYAML dependency is absent. The toolkit's dependency-free validator checks this known bundle shape, not arbitrary YAML or model behavior.

## Real native-agent demonstrations

These were actual separate agent threads, not mocked reviewers or fabricated ledger identities. Initial critics were spawned with `fork_turns="none"` and given the role, target and neutral review procedure. This setup is parent-observed provenance; the ledger cannot cryptographically prove context isolation.

### Software

Seed candidate: `average(values)` returned `sum(values) / len(values)` and its supplied suite covered only a simple nonempty input.

1. `/root/live_code_critic` independently found an empty-input division error and missing required regression cases. Its four-case verification exited 1.
2. `/root/live_developer` claimed the repair, implemented `None` for empty input, and added required tests.
3. The independent critic re-ran its four cases and the five delivered tests, then accepted the implementation.
4. `/root/live_validation` separately checked the integrated behavior and handoff. An initial malformed supplementary command failed due to quoting. The ledger refused approval despite a later passing command. The unchanged handoff was resubmitted with an explicit explanation; corrected checks passed and validation was accepted.
5. The CTO invoked the delivery gate successfully. Final state: **delivered**.

See [software evidence](evidence/software-review.json) and the runnable [example](../examples/software/average.py). This small case demonstrates workflow operation, not a general success rate.

### Machine learning

`/root/live_ml_critic` independently assessed a candidate evaluation against a requirement to predict previously unseen animals. It found train/test animal overlap and an absent separate baseline result. A real disjointness check failed; a repeatability check passed. It returned blocking/major findings and correctly left the candidate **needs_revision**. No ML repair or successful model result is claimed.

See [ML evidence](evidence/ml-review.json). The intentionally rejected candidate remains in local ignored runtime data; it is not shipped as a recommended ML implementation.

## Independent implementation review

A separate reviewer reproduced retry-limit bypass, research-mode dispatch bypass, stale dependency approvals, an unclosed SQLite connection, a pending-verification approval race, and stale external inspection evidence. These were corrected and regression-tested before delivery. A separate test author found an ownership conflict at review start; it was corrected and covered.

## Explicit limits

- Real execution above used supported native generic subagent threads with the authored role instructions. Structural validation does not prove the IDE has loaded custom role names in this already-open session; a new session is needed after activation.
- Python gates registered ledger operations. Host controls enforce permissions and actual context isolation. Semantic quality and truthful identities remain orchestration responsibilities.
- Recovery is explicit and reconciles saved state; there is no daemon, automatic restart service, or unattended scheduler.
- Global requirement changes conservatively invalidate all tasks. More precise impact analysis remains the CTO's responsibility.
- Complete provider billing is unavailable. Actual model token/cost efficiency has not been benchmarked; no hard monetary cap or cost-per-accepted-task claim is made.
- Shared knowledge uses approved, scoped local records and explicit sanitized transfer. It is not model retraining, automatic global synchronization, or an embedding-based memory service.
