"""Exercise delivery gates with disposable projects and real verification commands."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor


SPEC = importlib.util.spec_from_file_location("sr_team", Path(__file__).resolve().parents[1] / "team.py")
team = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(team)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("brief.md", "Deliver a verified implementation and reviewed handoff.\n")
        self.ledger = team.Ledger(self.root)
        self.ledger.init(self.root / "brief.md")

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def act(self, action, actor="cto", **fields):
        return self.ledger.apply(dict(action=action, actor=actor, **fields))

    def task(self, key="code", files=None, deps=None, stage="implementation"):
        return self.act("task", id=key, purpose="Produce independently verified work",
                        approach="Producer implementation followed by independent review",
                        owner_role="engineer", critic_role="reviewer", profile="software",
                        stage=stage, acceptance=["Verification succeeds"],
                        files=files or [key + ".txt"], depends_on=deps or [])

    def submit(self, key="code", actor="producer"):
        token = self.act("claim", actor, id=key)["token"]
        self.act("submit", actor, id=key, token=token, summary="PRIVATE producer rationale")
        return token

    def reviewing(self, key="code"):
        self.submit(key)
        return self.act("review_start", "critic", id=key)["token"]

    def inspect(self, key, token, evidence=None):
        return self.act("inspection", "critic", id=key, token=token,
                        summary="Read artifacts against the acceptance criteria",
                        evidence=evidence or self.ledger.status()["tasks"][key]["files"])

    def verdict(self, key, token, verdict="approve", findings=None):
        return self.act("review", "critic", id=key, token=token, verdict=verdict,
                        summary="Independent result", findings=findings or [])

    def finding(self, evidence="Verifier returned nonzero"):
        return dict(id="F1", severity="major", evidence=evidence,
                    impact="Acceptance criterion fails", verification="Rerun independent verifier")

    def accept(self, key):
        token = self.reviewing(key)
        self.inspect(key, token)
        self.verdict(key, token)

    def test_lifecycle_requires_separate_critic_evidence_and_reviewed_handoff(self):
        self.write("code.txt", "implementation")
        self.task()
        producer_token = self.submit()
        with self.assertRaisesRegex(team.TeamError, "critic"):
            self.act("review_start", "producer", id="code")
        review = self.act("review_start", "critic", id="code")
        self.assertNotIn("PRIVATE", json.dumps(review["packet"]))
        self.assertNotIn("approach", review["packet"])
        with self.assertRaises(team.TeamError):
            self.act("submit", "producer", id="code", token=producer_token, summary="late")
        with self.assertRaisesRegex(team.TeamError, "evidence"):
            self.verdict("code", review["token"])
        self.inspect("code", review["token"])
        result = self.ledger.check("code", "critic", review["token"],
                                   [sys.executable, "-c", "from pathlib import Path; assert Path('code.txt').read_text() == 'implementation'"])
        self.assertTrue(result["passed"])
        self.verdict("code", review["token"])
        with self.assertRaisesRegex(team.TeamError, "validation"):
            self.act("deliver", handoff="code.txt")
        self.write("handoff.md", "Verified implementation; deployment instructions.")
        self.task("validation", ["handoff.md"], ["code"], "validation")
        self.accept("validation")
        self.write("unreviewed.md", "unreviewed")
        with self.assertRaisesRegex(team.TeamError, "reviewed"):
            self.act("deliver", handoff="unreviewed.md")
        self.assertEqual("delivered", self.act("deliver", handoff="handoff.md")["status"])
        self.assertEqual("delivered", team.Ledger(self.root).status()["status"])

    def test_real_code_defect_is_detected_then_fixed_in_bounded_revision(self):
        self.task(files=["sum.py"])
        self.write("sum.py", "def add(a, b): return a - b\n")
        token = self.reviewing()
        argv = [sys.executable, "-c", "exec(open('sum.py').read()); assert add(3, 2) == 5"]
        check = self.ledger.check("code", "critic", token, argv)
        self.assertFalse(check["passed"])
        self.assertIn("AssertionError", check["output"])
        with self.assertRaisesRegex(team.TeamError, "must pass"):
            self.verdict("code", token)
        self.verdict("code", token, "revise", [self.finding(check["output"])])
        producer = self.act("claim", "producer", id="code")["token"]
        self.write("sum.py", "def add(a, b): return a + b\n")
        self.act("submit", "producer", id="code", token=producer, summary="Correct addition")
        token = self.act("review_start", "critic", id="code")["token"]
        self.assertTrue(self.ledger.check("code", "critic", token, argv)["passed"])
        self.assertEqual("accepted", self.verdict("code", token)["status"])
        self.assertEqual(1, self.ledger.status()["tasks"]["code"]["rounds"])

    def test_revision_limit_blocks_instead_of_looping(self):
        self.act("budget", limits={"max_revisions": 1}, reason="Bound retries")
        self.write("code.txt", "broken")
        self.task()
        for expected in ("needs_revision", "blocked"):
            token = self.reviewing()
            self.assertEqual(expected, self.verdict("code", token, "revise", [self.finding()])["status"])
        with self.assertRaises(team.TeamError):
            self.act("claim", "producer", id="code")
        self.task()
        with self.assertRaisesRegex(team.TeamError, "attempt budget"):
            self.act("claim", "replacement-producer", id="code")
        self.act("budget", limits={"max_revisions": 2}, reason="Authorize one more implementation attempt")
        self.act("claim", "replacement-producer", id="code")

    def test_prior_producer_cannot_review_replacement_producers_work(self):
        self.write("code.txt", "work")
        self.task()
        token = self.reviewing()
        self.verdict("code", token, "revise", [self.finding()])
        self.submit(actor="replacement-producer")
        with self.assertRaisesRegex(team.TeamError, "critic"):
            self.act("review_start", "producer", id="code")

    def test_research_mode_rejects_preexisting_implementation_task(self):
        self.task()
        self.act("mode", mode="research", reason="Investigate before implementing")
        with self.assertRaisesRegex(team.TeamError, "Research mode"):
            self.act("claim", "producer", id="code")

    def test_replanning_dependency_revokes_descendant_tokens_even_with_same_bytes(self):
        self.write("a.txt", "unchanged bytes")
        self.write("b.txt", "dependent work")
        self.task("a")
        self.accept("a")
        self.task("b", deps=["a"])
        token = self.act("claim", "producer", id="b")["token"]
        self.act("block", id="a", reason="Acceptance needs deeper analysis")
        self.task("a")
        self.accept("a")
        with self.assertRaises(team.TeamError):
            self.act("submit", "producer", id="b", token=token, summary="Based on old acceptance")
        self.assertEqual("stale", self.ledger.status()["tasks"]["b"]["status"])

    def test_ml_fixture_leakage_check_finds_shared_subjects(self):
        self.task("ml", ["split.json"])
        self.write("split.json", json.dumps({"train": ["patient1", "patient2"], "test": ["patient2", "patient3"]}))
        token = self.reviewing("ml")
        argv = [sys.executable, "-c", "import json; d=json.load(open('split.json')); overlap=set(d['train']) & set(d['test']); assert not overlap, 'subject leakage: '+str(sorted(overlap))"]
        result = self.ledger.check("ml", "critic", token, argv)
        self.assertFalse(result["passed"])
        self.assertIn("patient2", result["output"])
        self.verdict("ml", token, "revise", [self.finding(result["output"])])
        producer = self.act("claim", "producer", id="ml")["token"]
        self.write("split.json", json.dumps({"train": ["patient1", "patient2"], "test": ["patient3"]}))
        self.act("submit", "producer", id="ml", token=producer, summary="Split subjects exclusively")
        token = self.act("review_start", "critic", id="ml")["token"]
        self.assertTrue(self.ledger.check("ml", "critic", token, argv)["passed"])
        self.verdict("ml", token)

    def test_requirement_change_revokes_both_assignment_types(self):
        self.task("running")
        producer = self.act("claim", "producer", id="running")["token"]
        self.write("reviewed.txt", "work")
        self.task("reviewed")
        critic = self.reviewing("reviewed")
        self.write("business_requirement.md", "Changed acceptance requirements")
        with self.assertRaisesRegex(team.TeamError, "requirements changed"):
            self.inspect("reviewed", critic)
        with self.assertRaises(team.TeamError):
            self.act("change", reason="New requirement")
        self.act("change", workers_stopped=True, reason="New requirement")
        with self.assertRaises(team.TeamError):
            self.act("submit", "producer", id="running", token=producer, summary="late")
        with self.assertRaises(team.TeamError):
            self.verdict("reviewed", critic)
        self.assertTrue(all(t["status"] == "stale" and t["token"] is None and t["review_token"] is None
                            for t in self.ledger.status()["tasks"].values()))

    def test_recovery_revokes_interrupted_tokens_and_requires_stopped_workers(self):
        self.write("code.txt", "work")
        self.task()
        old = self.act("claim", "producer", id="code")["token"]
        self.act("pause")
        self.ledger = team.Ledger(self.root)
        with self.assertRaises(team.TeamError):
            self.act("recover")
        self.act("recover", workers_stopped=True)
        new = self.act("claim", "producer", id="code")["token"]
        self.assertNotEqual(old, new)
        with self.assertRaises(team.TeamError):
            self.act("submit", "producer", id="code", token=old, summary="late")
        self.act("submit", "producer", id="code", token=new, summary="current")
        critic = self.act("review_start", "critic", id="code")["token"]
        self.act("pause")
        self.act("recover", workers_stopped=True)
        with self.assertRaises(team.TeamError):
            self.inspect("code", critic)

    def test_simultaneous_overlapping_claims_have_exactly_one_winner(self):
        self.task("a", ["shared.txt"])
        self.task("b", ["shared.txt"])
        barrier = threading.Barrier(2)
        def claim(key):
            barrier.wait(timeout=5)
            try:
                team.Ledger(self.root).apply(dict(action="claim", actor=key, id=key))
                return "won"
            except team.TeamError as error:
                return str(error)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(claim, ["a", "b"]))
        self.assertEqual(1, results.count("won"))
        self.assertTrue(any("ownership conflict" in value for value in results))
        self.assertEqual(1, self.ledger.status()["claims"])

    def test_review_cannot_start_while_another_producer_owns_same_artifact(self):
        self.write("shared.txt", "work")
        self.task("a", ["shared.txt"])
        self.task("b", ["shared.txt"])
        self.submit("a")
        self.act("claim", "other-producer", id="b")
        with self.assertRaisesRegex(team.TeamError, "ownership conflict"):
            self.act("review_start", "critic", id="a")

    def test_claim_check_research_and_experiment_budgets_are_consumed(self):
        self.act("budget", reason="Strict limits", limits={"max_claims": 2, "max_checks": 1, "max_research": 1, "max_experiments": 1})
        self.write("code.txt", "work")
        self.task()
        token = self.reviewing()
        self.ledger.check("code", "critic", token, [sys.executable, "-c", "pass"])
        with self.assertRaisesRegex(team.TeamError, "Check budget"):
            self.ledger.check("code", "critic", token, [sys.executable, "-c", "pass"])
        self.verdict("code", token, "revise", [self.finding()])
        with self.assertRaisesRegex(team.TeamError, "activation budget"):
            self.act("claim", "producer", id="code")
        for kind in ("research", "experiments"):
            self.act("reserve", kind=kind)
            with self.assertRaisesRegex(team.TeamError, "budget exhausted"):
                self.act("reserve", kind=kind)
        self.assertEqual(1, self.ledger.status()["checks_used"])

    def test_active_limit_and_check_timeout_are_enforced(self):
        self.act("budget", reason="One worker and one second per check",
                 limits={"max_active": 1, "max_check_seconds": 1})
        self.write("code.txt", "work")
        self.task()
        self.task("other")
        token = self.reviewing()
        with self.assertRaisesRegex(team.TeamError, "Concurrency limit"):
            self.act("claim", "another-producer", id="other")
        result = self.ledger.check("code", "critic", token,
                                   [sys.executable, "-c", "import time; time.sleep(10)"])
        self.assertFalse(result["passed"])
        self.assertIn("timed out", result["output"])
        with self.assertRaisesRegex(team.TeamError, "must pass"):
            self.verdict("code", token)

    def test_dependency_cycles_and_changed_dependency_prevent_work(self):
        self.task("a")
        self.task("b", deps=["a"])
        with self.assertRaisesRegex(team.TeamError, "cycle"):
            self.task("a", deps=["b"])
        with self.assertRaisesRegex(team.TeamError, "incomplete or stale"):
            self.act("claim", "producer", id="b")
        self.write("a.txt", "reviewed")
        self.accept("a")
        self.write("a.txt", "changed after review")
        with self.assertRaisesRegex(team.TeamError, "incomplete or stale"):
            self.act("claim", "producer", id="b")
        recovered = self.act("recover", workers_stopped=True)
        self.assertEqual(["a", "b"], recovered["replan"])

    def test_mutation_during_check_and_stale_inspection_cannot_approve(self):
        self.write("code.txt", "work")
        self.task()
        token = self.reviewing()
        with self.assertRaisesRegex(team.TeamError, "modified or raced"):
            self.ledger.check("code", "critic", token, [sys.executable, "-c", "from pathlib import Path; Path('code.txt').write_text('changed')"])
        with self.assertRaises(team.TeamError):
            self.verdict("code", token)
        self.write("other.txt", "work")
        self.task("other")
        other_token = self.reviewing("other")
        self.write("evidence.txt", "verified")
        self.inspect("other", other_token, ["evidence.txt"])
        self.write("evidence.txt", "changed")
        with self.assertRaisesRegex(team.TeamError, "evidence changed"):
            self.verdict("other", other_token)

    def test_lessons_require_independent_review_deduplicate_and_retire(self):
        lesson = dict(problem="Shared patient IDs", cause="Row split", correction="Split by patient",
                      applicability="Repeated subject data", evidence="Failing overlap verifier",
                      prevention="Check disjoint IDs", scope="specialist")
        self.act("lesson_propose", "producer", id="leakage", **lesson)
        with self.assertRaisesRegex(team.TeamError, "Independent"):
            self.act("lesson_review", "producer", id="leakage", approved=True, evidence="self review")
        self.act("lesson_review", "critic", id="leakage", approved=True, evidence="Reproduced leakage")
        with self.assertRaisesRegex(team.TeamError, "Duplicate"):
            self.act("lesson_propose", "another", id="duplicate", **(lesson | {"problem": " SHARED PATIENT IDS "}))
        self.act("lesson_retire", id="leakage", reason="Superseded with group splitting guidance")
        self.act("lesson_propose", "another", id="replacement", **lesson)
        self.assertEqual("proposed", self.ledger.status()["lessons"]["replacement"]["status"])

    def test_paths_cannot_escape_project_or_target_ledger_and_brief(self):
        for path in ("../escape.txt", str(self.root.parent / "absolute.txt"),
                     ".startup-team/state.sqlite3", "nested/../../escape.txt", "business_requirement.md"):
            with self.subTest(path=path), self.assertRaises(team.TeamError):
                self.task(files=[path])
        self.assertEqual({}, self.ledger.status()["tasks"])

    def test_pending_real_subprocess_prevents_approval_until_failure_is_recorded(self):
        self.write("code.txt", "work")
        self.task()
        token = self.reviewing()
        self.inspect("code", token)
        self.act("budget", limits={"max_check_seconds": 5}, reason="Bound concurrent regression")
        command = "from pathlib import Path\nimport time\nPath('started').touch()\nwhile not Path('release').exists(): time.sleep(0.01)\nraise SystemExit(7)"
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.ledger.check, "code", "critic", token, [sys.executable, "-c", command])
            try:
                deadline = time.monotonic() + 4
                while not (self.root / "started").exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue((self.root / "started").exists(), "Verifier did not start")
                with self.assertRaisesRegex(team.TeamError, "pending"):
                    self.verdict("code", token)
            finally:
                self.write("release", "continue")
            self.assertEqual(7, future.result(timeout=5)["exit_code"])
        with self.assertRaisesRegex(team.TeamError, "must pass"):
            self.verdict("code", token)

    def test_stale_external_inspection_evidence_blocks_delivery_and_recovery(self):
        self.write("handoff.md", "Reviewed handoff")
        self.write("evidence.txt", "Independent evaluation")
        self.task("validation", ["handoff.md"], stage="validation")
        token = self.reviewing("validation")
        self.inspect("validation", token, ["evidence.txt"])
        self.verdict("validation", token)
        self.write("evidence.txt", "Evaluation withdrawn")
        with self.assertRaisesRegex(team.TeamError, "evidence changed"):
            self.act("deliver", handoff="handoff.md")
        self.assertEqual(["validation"], self.act("recover", workers_stopped=True)["replan"])

    def test_transfer_only_reviewed_safe_reusable_lessons_and_require_local_review(self):
        base = dict(cause="Root cause", correction="Check groups", applicability="Grouped data",
                    evidence="PRIVATE source project evidence", prevention="Automated verification")
        for key, scope, approved, safe in (("safe", "specialist", True, True),
                                            ("private", "project", True, True),
                                            ("unsafe", "team", True, False),
                                            ("unreviewed", "team", False, True)):
            self.act("lesson_propose", "producer", id=key, problem=key, scope=scope, **base)
            if approved:
                self.act("lesson_review", "critic", id=key, approved=True,
                         transfer_safe=safe, evidence="Independent review")
        package = self.root / "knowledge.json"
        self.assertEqual(1, self.ledger.transfer(package)["exported"])
        self.assertNotIn("PRIVATE", package.read_text(encoding="utf-8"))
        target = self.root / "target"
        target.mkdir()
        imported = team.Ledger(target)
        imported.init(self.root / "brief.md")
        imported.import_lessons(package, "importer")
        self.assertEqual([], imported.knowledge())
        with self.assertRaises(team.TeamError):
            imported.apply(dict(action="lesson_review", actor="importer", id="safe", approved=True, evidence="Self review"))
        imported.apply(dict(action="lesson_review", actor="local-critic", id="safe", approved=True, evidence="Verified local applicability"))
        self.assertEqual(["safe"], [lesson["id"] for lesson in imported.knowledge()])


if __name__ == "__main__":
    unittest.main()
