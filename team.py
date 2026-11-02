#!/usr/bin/env python3
"""Portable delivery ledger. Python 3.11+, standard library only.

This program records and gates work; Codex performs agent orchestration.
It does not authenticate agent identities or sandbox subprocesses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
import subprocess
import sys
import time
import uuid
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path


class TeamError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise TeamError(message)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def confined(root, name):
    require(isinstance(name, str) and name, "A relative file path is required")
    require(not Path(name).is_absolute(), "Absolute artifact paths are not allowed")
    path = (root / name).resolve()
    require(path.is_relative_to(root), "Path escapes the project root")
    require(not path.is_relative_to(root / ".startup-team"), "Ledger files are not task artifacts")
    return path


def snapshot(root, files):
    require(isinstance(files, list) and files, "Declare at least one owned artifact")
    result = {}
    for name in files:
        path = confined(root, name)
        require(path.is_file(), f"Missing artifact: {name}")
        result[path.relative_to(root).as_posix()] = digest(path)
    return result


def unchanged(root, hashes):
    return bool(hashes) and all(confined(root, name).is_file() and digest(confined(root, name)) == value
                                for name, value in hashes.items())


def evidence_fresh(root, task):
    return all(unchanged(root, c["evidence"]) for c in task.get("checks", []) if c.get("evidence"))


DEFAULTS = {"mode": "collaborative", "max_active": 2, "max_claims": 40,
            "max_revisions": 2, "max_check_seconds": 120, "max_checks": 60,
            "max_research": 8, "max_experiments": 8, "deadline_seconds": 14400}


class Ledger:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.db = self.root / ".startup-team" / "state.sqlite3"

    def init(self, brief, config=None):
        require(self.root.is_dir(), "Project root must exist")
        require(not self.db.exists(), "Project already initialized")
        config = dict(config or {})
        require(not set(config) - set(DEFAULTS), "Unknown configuration field")
        config = DEFAULTS | config
        require(config["mode"] in {"collaborative", "autonomous", "research"}, "Invalid mode")
        for key, value in config.items():
            if key != "mode":
                require(type(value) is int and value > 0, f"{key} must be a positive integer")
        source = Path(brief).resolve()
        require(source.is_file(), "Business requirement file missing")
        target = self.root / "business_requirement.md"
        if target.exists():
            require(target.read_bytes() == source.read_bytes(), "Existing business requirement differs; refusing overwrite")
        else:
            target.write_bytes(source.read_bytes())
        self.db.parent.mkdir(exist_ok=True)
        state = {"schema_version": 1, "project_id": str(uuid.uuid4()), "created": timestamp(),
                 "status": "active", "revision": 1, "brief_hash": digest(target),
                 "config": config, "deadline": time.time() + config["deadline_seconds"],
                 "claims": 0, "checks_used": 0, "research_used": 0, "experiments_used": 0,
                 "tasks": {}, "lessons": {}, "decisions": [], "usage": [], "events": []}
        with closing(sqlite3.connect(self.db)) as con:
            with con:
                con.execute("CREATE TABLE state (id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL)")
                con.execute("INSERT INTO state VALUES(1, ?)", (json.dumps(state, ensure_ascii=False),))
        return self.status()

    @contextmanager
    def transaction(self):
        require(self.db.is_file(), "Initialize this project first")
        con = sqlite3.connect(self.db, timeout=10)
        try:
            con.execute("BEGIN IMMEDIATE")
            state = json.loads(con.execute("SELECT body FROM state WHERE id=1").fetchone()[0])
            yield state
            con.execute("UPDATE state SET body=? WHERE id=1", (json.dumps(state, ensure_ascii=False),))
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def status(self):
        with self.transaction() as state:
            result = json.loads(json.dumps(state))
        result["brief_changed"] = not (self.root / "business_requirement.md").is_file() or digest(self.root / "business_requirement.md") != result["brief_hash"]
        result["stale_artifacts"] = [key for key, task in result["tasks"].items()
                                     if task.get("hashes") and not unchanged(self.root, task["hashes"])]
        values = [item["usd"] for item in result["usage"]]
        result["reported_cost_usd"] = sum(values) if values and all(v is not None for v in values) else None
        result["cost_scope"] = "reported entries only; complete platform billing is unavailable"
        feedback = result.get("feedback", [])
        latest = {(f["task"], f["revision"]): f for f in feedback}
        accepted = sum(f["accepted"] for f in latest.values())
        result["metrics"] = {
            "reviewed_task_outcomes": len(latest), "accepted_task_outcomes": accepted,
            "acceptance_rate": accepted / len(latest) if latest else None,
            "human_review_minutes": sum(f["human_minutes"] for f in feedback) if feedback else None,
            "repeat_mistakes_reported": sum(f["repeat_mistake"] for f in feedback) if feedback else None,
            "repair_rounds": sum(t["rounds"] for t in result["tasks"].values()),
            "cost_per_accepted_task": None,
            "note": "Acceptance uses explicit feedback, latest per task and requirement revision. Human effort sums feedback entries. Billing coverage is incomplete, so cost per accepted task is unknown."
        }
        return result

    def event(self, state, action, actor, details):
        state["events"].append({"time": timestamp(), "action": action, "actor": actor, "details": details})

    def fresh(self, state):
        path = self.root / "business_requirement.md"
        require(path.is_file() and digest(path) == state["brief_hash"], "Business requirements changed; run change and replan")

    def active(self, state):
        self.fresh(state)
        require(state["status"] == "active", f"Project is {state['status']}")
        require(time.time() < state["deadline"], "Runtime budget exhausted; explicitly extend the budget")

    def deps_fresh(self, state, task):
        for key in task["depends_on"]:
            dep = state["tasks"][key]
            require(dep["status"] == "accepted" and unchanged(self.root, dep.get("hashes", {})) and evidence_fresh(self.root, dep), f"Dependency {key} is incomplete or stale")
            if key in task.get("dependency_versions", {}):
                require(task["dependency_versions"][key] == dep["hashes"], f"Dependency {key} changed since assignment")
            self.deps_fresh(state, dep)

    def invalidate(self, state, ids, reason):
        affected = set(ids)
        while True:
            more = {key for key, task in state["tasks"].items() if affected.intersection(task["depends_on"])}
            if more <= affected:
                break
            affected |= more
        for key in affected:
            task = state["tasks"][key]
            task.update(status="stale", token=None, review_token=None, block_reason=reason)
        if affected and state["status"] == "delivered":
            state["status"] = "paused"
        return sorted(affected)

    def packet(self, state, task):
        # Deliberately excludes producer rationale, logs, past reviews and private conversations.
        return {"task_id": task["id"], "project_revision": state["revision"],
                "business_requirement": (self.root / "business_requirement.md").read_text(encoding="utf-8-sig"),
                "purpose": task["purpose"], "acceptance": task["acceptance"],
                "profile": task["profile"], "stage": task["stage"],
                "artifacts": task.get("hashes", {}),
                "dependencies": [{"id": key, "acceptance": state["tasks"][key]["acceptance"],
                                  "artifacts": state["tasks"][key].get("hashes", {})}
                                 for key in task["depends_on"]],
                "instruction": "Assess independently before reading the producer's rationale. Inspect artifacts and verify requirements. Return evidence, impact and verification per finding. No edits to producer artifacts."}

    def apply(self, request):
        require(isinstance(request, dict), "Request must be an object")
        action, actor = request.get("action"), request.get("actor")
        require(isinstance(action, str) and action, "action must be a nonempty string")
        require(isinstance(actor, str) and actor.strip(), "actor must identify the actual agent thread or user")
        with self.transaction() as s:
            result = self._apply(s, request, action, actor)
            self.event(s, action, actor, request)
            return result

    def _apply(self, s, r, action, actor):
        if action == "task":
            self.active(s)
            key = r["id"]
            require(isinstance(key, str) and key.strip(), "Task id required")
            old = s["tasks"].get(key)
            require(not old or old["status"] in {"pending", "stale", "blocked"}, "Cannot replace active or accepted task")
            for field in ("purpose", "approach", "owner_role", "critic_role", "profile", "stage"):
                require(isinstance(r.get(field), str) and r[field].strip(), f"Missing {field}")
            require(isinstance(r.get("acceptance"), list) and r["acceptance"] and all(isinstance(x, str) and x.strip() for x in r["acceptance"]), "Acceptance criteria required")
            require(r["stage"] in {"requirements", "design", "planning", "implementation", "validation"}, "Invalid stage")
            require(s["config"]["mode"] != "research" or r["stage"] != "implementation", "Research mode cannot dispatch implementation")
            files = r.get("files", [])
            require(isinstance(files, list) and files, "Explicit file ownership required")
            files = [confined(self.root, f).relative_to(self.root).as_posix() for f in files]
            require("business_requirement.md" not in files, "Agents must preserve the original business requirement")
            deps = r.get("depends_on", [])
            require(isinstance(deps, list) and all(d in s["tasks"] and d != key for d in deps), "Dependencies must already exist and cannot include self")
            def reaches(dep):
                return dep == key or any(reaches(x) for x in s["tasks"][dep]["depends_on"])
            require(not any(reaches(d) for d in deps), "Dependency cycle")
            if old:
                self.invalidate(s, [key], "Task specification was replaced")
            s["tasks"][key] = {k: r[k] for k in ("purpose", "approach", "owner_role", "critic_role", "profile", "stage", "acceptance")}
            s["tasks"][key].update(id=key, files=files, depends_on=deps, revision=s["revision"],
                                   status="pending", rounds=(old or {}).get("rounds", 0),
                                   attempts=(old or {}).get("attempts", 0), producers=(old or {}).get("producers", []), checks=[], reviews=[])
            return s["tasks"][key]
        if action in {"pause", "stop"}:
            s["status"] = "paused" if action == "pause" else "stopped"
            for task in s["tasks"].values():
                if task["status"] in {"running", "reviewing"}:
                    task.update(status="interrupted", token=None, review_token=None)
            return {"status": s["status"], "notice": "Native workers must also be interrupted by the CTO; this ledger cannot kill them."}
        if action == "recover":
            self.fresh(s)
            require(s["status"] != "delivered", "Delivery is complete")
            require(r.get("workers_stopped") is True, "Confirm all previous native workers have stopped")
            for task in s["tasks"].values():
                if task["status"] in {"running", "reviewing", "interrupted"}:
                    task.update(status="pending", token=None, review_token=None)
            changed = [key for key, task in s["tasks"].items() if task.get("hashes") and (not unchanged(self.root, task["hashes"]) or not evidence_fresh(self.root, task))]
            invalid = self.invalidate(s, changed, "Artifact changed since checkpoint")
            s["status"] = "active"
            return {"status": "active", "replan": invalid}
        if action == "change":
            require(r.get("reason"), "Explain the requirement change")
            require(r.get("workers_stopped") is True, "Stop workers before changing the revision")
            path = self.root / "business_requirement.md"
            require(path.is_file(), "Business requirement is missing")
            s["brief_hash"] = digest(path)
            s["revision"] += 1
            result = self.invalidate(s, list(s["tasks"]), r["reason"])
            s["status"] = "active"
            return {"revision": s["revision"], "replan": result}
        if action == "budget":
            require(r.get("reason"), "Budget changes need a reason and existing authority")
            for key, value in r.get("limits", {}).items():
                require(key in DEFAULTS and key != "mode" and type(value) is int and value > 0, "Invalid budget limit")
                s["config"][key] = value
                if key == "deadline_seconds":
                    s["deadline"] = time.time() + value
            return s["config"]
        if action == "mode":
            require(r.get("mode") in {"collaborative", "autonomous", "research"}, "Invalid mode")
            require(r.get("reason"), "Explain mode change")
            require(not any(t["status"] in {"running", "reviewing"} for t in s["tasks"].values()), "Pause active workers before changing modes")
            s["config"]["mode"] = r["mode"]
            return {"mode": r["mode"]}
        if action == "usage":
            value = r.get("usd")
            require(value is None or type(value) in {int, float} and math.isfinite(value) and value >= 0, "Invalid reported cost")
            s["usage"].append({"actor": actor, "usd": value, "source": r.get("source", "unknown"), "time": timestamp()})
            return s["usage"][-1]
        if action == "feedback":
            require(r.get("task") in s["tasks"], "Feedback must reference an existing task")
            require(type(r.get("accepted")) is bool and type(r.get("repeat_mistake")) is bool, "Feedback needs boolean accepted and repeat_mistake")
            minutes = r.get("human_minutes")
            require(type(minutes) in {int, float} and math.isfinite(minutes) and minutes >= 0, "Actual human review minutes required")
            require(r.get("source"), "Identify the source of measured feedback")
            record = {k: r[k] for k in ("task", "accepted", "repeat_mistake", "human_minutes", "source")}
            record.update(actor=actor, revision=s["revision"], time=timestamp())
            s.setdefault("feedback", []).append(record)
            return record
        if action == "decision":
            for field in ("question", "choice", "reason", "alternatives", "sources"):
                require(field in r, f"Missing decision {field}")
            s["decisions"].append(r | {"time": timestamp(), "revision": s["revision"]})
            return s["decisions"][-1]
        if action == "reserve":
            self.active(s)
            kind = r.get("kind")
            require(kind in {"research", "experiments"}, "Reserve research or experiments")
            require(s[kind + "_used"] < s["config"]["max_" + kind], f"{kind} budget exhausted")
            s[kind + "_used"] += 1
            return {"used": s[kind + "_used"]}
        if action.startswith("lesson_"):
            return self.lesson(s, r, action, actor)
        if action == "deliver":
            self.active(s)
            require(s["tasks"] and all(t["status"] == "accepted" for t in s["tasks"].values()), "All tasks must be accepted")
            require(any(t["stage"] == "validation" for t in s["tasks"].values()), "An independent validation task is required")
            for task in s["tasks"].values():
                require(unchanged(self.root, task["hashes"]), "Artifact changed after acceptance")
                require(evidence_fresh(self.root, task), "Inspection evidence changed after acceptance")
                self.deps_fresh(s, task)
            require(r.get("handoff"), "Provide a handoff artifact")
            hashes = snapshot(self.root, [r["handoff"]])
            require(all(any(t["hashes"].get(k) == v for t in s["tasks"].values()) for k, v in hashes.items()), "Handoff must be part of reviewed artifacts")
            s["status"] = "delivered"
            return {"status": "delivered", "handoff": r["handoff"]}

        require(r.get("id") in s["tasks"], "Unknown task")
        task = s["tasks"][r["id"]]
        if action == "packet":
            self.fresh(s)
            require(task["status"] in {"review", "reviewing"}, "Submit work before review")
            require(unchanged(self.root, task["hashes"]), "Artifact changed; resubmit")
            return self.packet(s, task)
        if action == "block":
            require(r.get("reason"), "Block reason required")
            self.invalidate(s, [task["id"]], r["reason"])
            task.update(status="blocked", block_reason=r["reason"], token=None, review_token=None)
            return task
        self.active(s)
        require(task["revision"] == s["revision"], "Task specification is stale")
        self.deps_fresh(s, task)
        if action in {"claim", "review_start"}:
            busy = [t for t in s["tasks"].values() if t["status"] in {"running", "reviewing"}]
            require(len(busy) < s["config"]["max_active"], "Concurrency limit reached")
            require(s["claims"] < s["config"]["max_claims"], "Agent activation budget exhausted")
            owned = {confined(self.root, f) for f in task["files"]}
            require(not any(owned.intersection(confined(self.root, f) for f in t["files"]) for t in busy), "Artifact ownership conflict")
            token = str(uuid.uuid4())
            if action == "claim":
                require(s["config"]["mode"] != "research" or task["stage"] != "implementation", "Research mode cannot dispatch implementation")
                require(task["status"] in {"pending", "needs_revision"}, "Task cannot be claimed")
                require(task["attempts"] < s["config"]["max_revisions"] + 1, "Task attempt budget exhausted; coordinator must explicitly extend it")
                if task["status"] == "needs_revision":
                    require(task["rounds"] < s["config"]["max_revisions"], "Revision budget exhausted")
                    task["rounds"] += 1
                task["attempts"] += 1
                if actor not in task["producers"]:
                    task["producers"].append(actor)
                task.update(status="running", owner=actor, token=token, review_token=None, checks=[], pending_check=None)
                task["dependency_versions"] = {d: dict(s["tasks"][d]["hashes"]) for d in task["depends_on"]}
            else:
                require(task["status"] == "review", "Task is not ready for review")
                require(actor not in task["producers"], "Any previous producer is ineligible as critic")
                require(unchanged(self.root, task["hashes"]), "Artifact changed; resubmit")
                task.update(status="reviewing", critic=actor, review_token=token)
            s["claims"] += 1
            return {"token": token, "packet": self.packet(s, task) if action == "review_start" else task}
        if action == "submit":
            require(task["status"] == "running" and task["owner"] == actor and task.get("token") == r.get("token"), "Stale or foreign producer result")
            require(r.get("summary"), "Provide a plain-language outcome")
            hashes = snapshot(self.root, task["files"])
            task.update(status="review", hashes=hashes, summary=r["summary"], checks=[], review_token=None)
            return {"status": "review", "hashes": hashes}
        if action == "inspection":
            require(task["status"] == "reviewing" and actor == task["critic"] and r.get("token") == task["review_token"], "Only assigned critic can record inspection")
            require(unchanged(self.root, task["hashes"]), "Artifact changed during review")
            require(r.get("summary") and r.get("evidence"), "Inspection needs explanation and evidence")
            evidence = snapshot(self.root, r["evidence"])
            task["checks"].append({"kind": "inspection", "actor": actor, "summary": r["summary"],
                                    "evidence": evidence, "hashes": task["hashes"], "passed": True, "time": timestamp()})
            return task["checks"][-1]
        if action == "review":
            require(task["status"] == "reviewing" and actor == task["critic"] and r.get("token") == task["review_token"], "Stale or foreign critic result")
            require(unchanged(self.root, task["hashes"]), "Artifact changed during review")
            require(not task.get("pending_check"), "A verification command is still pending")
            findings = r.get("findings")
            require(isinstance(findings, list), "findings must be a list")
            for finding in findings:
                require(all(finding.get(k) for k in ("id", "severity", "evidence", "impact", "verification")), "Incomplete finding")
                require(finding["severity"] in {"blocking", "major", "minor"}, "Invalid severity")
            verdict = r.get("verdict")
            require(verdict in {"approve", "revise"}, "Invalid review verdict")
            require(r.get("summary"), "Review summary required")
            if verdict == "approve":
                require(not any(f["severity"] in {"blocking", "major"} for f in findings), "Cannot approve unresolved material findings")
                checks = [c for c in task["checks"] if c["hashes"] == task["hashes"]]
                require(checks and all(c["passed"] for c in checks), "Current verification evidence must pass")
                require(all(unchanged(self.root, c["evidence"]) for c in checks if c.get("evidence")), "Inspection evidence changed")
                task["status"] = "accepted"
            else:
                require(findings, "Revision needs evidence-backed findings")
                task["status"] = "blocked" if task["rounds"] >= s["config"]["max_revisions"] else "needs_revision"
            task["reviews"].append(r | {"hashes": task["hashes"], "time": timestamp(), "verification": list(task["checks"])})
            task["review_token"] = None
            return {"status": task["status"], "rounds": task["rounds"]}
        raise TeamError(f"Unknown action: {action}")

    def lesson(self, s, r, action, actor):
        key = r.get("id")
        require(isinstance(key, str) and key, "Lesson id required")
        if action == "lesson_propose":
            require(key not in s["lessons"], "Lesson id already exists; retire and supersede instead")
            for field in ("problem", "cause", "correction", "applicability", "evidence", "prevention", "scope"):
                require(r.get(field), f"Missing lesson {field}")
            require(r["scope"] in {"project", "specialist", "team", "preference"}, "Invalid lesson scope")
            signature = hashlib.sha256((r["problem"].strip().casefold() + r["correction"].strip().casefold()).encode()).hexdigest()
            require(not any(x["signature"] == signature and x["status"] != "retired" for x in s["lessons"].values()), "Duplicate lesson")
            s["lessons"][key] = r | {"status": "proposed", "author": actor, "signature": signature, "project_id": s["project_id"]}
        else:
            require(key in s["lessons"], "Unknown lesson")
            lesson = s["lessons"][key]
            if action == "lesson_review":
                require(actor != lesson["author"] and lesson["status"] == "proposed", "Independent lesson review required")
                require(r.get("evidence") and isinstance(r.get("approved"), bool), "Review evidence and approval required")
                lesson.update(status="approved" if r["approved"] else "rejected", reviewer=actor, review_evidence=r["evidence"], transfer_safe=r.get("transfer_safe") is True)
            elif action == "lesson_retire":
                require(r.get("reason"), "Retirement reason required")
                lesson.update(status="retired", retirement_reason=r["reason"])
            else:
                raise TeamError("Unknown lesson action")
        return s["lessons"][key]

    def knowledge(self, query="", scope=None):
        terms = set(query.casefold().split())
        return [lesson for lesson in self.status()["lessons"].values()
                if lesson["status"] == "approved" and (not scope or lesson["scope"] == scope)
                and (not terms or terms.intersection((lesson["applicability"] + " " + lesson["problem"] + " " + lesson["correction"]).casefold().split()))]

    def transfer(self, destination):
        """Export only independently reviewed, explicitly sanitized reusable lessons."""
        lessons = self.knowledge()
        exported = []
        for lesson in lessons:
            if lesson["scope"] != "project" and lesson.get("transfer_safe"):
                fields = ("id", "problem", "cause", "correction", "applicability", "prevention", "scope")
                exported.append({k: lesson[k] for k in fields})
        path = Path(destination).resolve()
        require(not path.exists(), "Refusing to overwrite a knowledge export")
        path.write_text(json.dumps({"schema_version": 1, "lessons": exported}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"exported": len(exported), "file": str(path), "note": "Source evidence and project identity omitted; target project must review imported lessons."}

    def import_lessons(self, path, actor):
        require(isinstance(actor, str) and actor.strip(), "Importer actor required")
        data = read_json(path)
        require(isinstance(data, dict) and data.get("schema_version") == 1 and isinstance(data.get("lessons"), list), "Invalid knowledge package")
        with self.transaction() as s:
            results = []
            for item in data["lessons"]:
                require(isinstance(item, dict), "Every imported lesson must be an object")
                require(item.get("scope") in {"team", "specialist", "preference"}, "Project lessons cannot be imported")
                request = item | {"action": "lesson_propose", "actor": actor, "evidence": "Imported package; validate against current project before approval"}
                results.append(self.lesson(s, request, "lesson_propose", actor))
            self.event(s, "knowledge_import", actor, {"count": len(results), "package_sha256": digest(Path(path))})
            return results

    def check(self, key, actor, token, argv):
        require(isinstance(argv, list) and argv and all(isinstance(x, str) for x in argv), "Check command must be a nonempty JSON string array")
        with self.transaction() as s:
            self.active(s)
            require(key in s["tasks"], "Unknown task")
            task = s["tasks"][key]
            self.deps_fresh(s, task)
            require(task["status"] == "reviewing" and task["critic"] == actor and task["review_token"] == token, "Only assigned critic can run a check")
            require(unchanged(self.root, task["hashes"]), "Artifact changed before check")
            require(not task.get("pending_check"), "A verification command is already pending")
            require(s["checks_used"] < s["config"]["max_checks"], "Check budget exhausted")
            s["checks_used"] += 1
            check_id = str(uuid.uuid4())
            task["pending_check"] = {"id": check_id, "argv": argv, "started": timestamp()}
            before = dict(task["hashes"])
            timeout = min(s["config"]["max_check_seconds"], max(0.01, s["deadline"] - time.time()))
        try:
            completed = subprocess.run(argv, cwd=self.root, shell=False, capture_output=True, timeout=timeout)
            code = completed.returncode
            output = (completed.stdout + completed.stderr).decode("utf-8", errors="replace")[-12000:]
        except subprocess.TimeoutExpired:
            code, output = -1, "Check timed out"
        except OSError as error:
            code, output = -1, str(error)
        with self.transaction() as s:
            self.active(s)
            task = s["tasks"][key]
            self.deps_fresh(s, task)
            require(task["status"] == "reviewing" and task["review_token"] == token, "Check completed after its assignment was invalidated")
            require(task.get("pending_check", {}).get("id") == check_id, "Check reservation is stale")
            require(unchanged(self.root, before), "Check modified or raced with task artifacts; resubmit")
            evidence = {"kind": "command", "argv": argv, "exit_code": code, "output": output,
                        "hashes": before, "passed": code == 0, "actor": actor, "time": timestamp()}
            task["checks"].append(evidence)
            task["pending_check"] = None
            self.event(s, "check", actor, {"task": key, **evidence})
        return evidence

    def export(self):
        s = self.status()
        lines = ["# Delivery status", "", f"Project: {s['project_id']}", f"Status: {s['status']}; requirement revision: {s['revision']}",
                 f"Agent claims: {s['claims']}/{s['config']['max_claims']}; reported cost: {s['reported_cost_usd']}", ""]
        for key, task in s["tasks"].items():
            lines += [f"## {key}: {task['status']}", "", task["purpose"], "", "Acceptance:"]
            lines += [f"- {x}" for x in task["acceptance"]]
            lines += ["", "Proposed approach: " + task["approach"], "", "Latest outcome: " + task.get("summary", "Not submitted"), ""]
            for review in task["reviews"]:
                lines += [f"Review ({review['verdict']}): {review['summary']}"]
                lines += [f"- {f['id']} [{f['severity']}]: {f['impact']} Evidence: {f['evidence']}" for f in review["findings"]]
            lines += [""]
        lines += ["## Event history", ""]
        lines += [f"- {e['time']} {e['actor']}: {e['action']} {json.dumps(e['details'], ensure_ascii=False)}" for e in s["events"]]
        target = self.db.parent / "history.md"
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"history": str(target)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Target project root; contains business_requirement.md")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Preserve a business brief and initialize a local ledger")
    init.add_argument("--brief", required=True)
    init.add_argument("--config", help="Optional JSON config; defaults documented in README")
    request = sub.add_parser("request", help="Apply one typed JSON action; see examples/requests")
    request.add_argument("--file", required=True)
    status = sub.add_parser("status", help="Compact progress and metrics; use --full for the complete ledger")
    status.add_argument("--full", action="store_true")
    sub.add_parser("export", help="Generate readable task and decision history")
    knowledge = sub.add_parser("knowledge", help="Retrieve only approved relevant lessons")
    knowledge.add_argument("--query", default="")
    knowledge.add_argument("--scope", choices=["project", "team", "specialist", "preference"])
    transfer = sub.add_parser("knowledge-export", help="Export independently approved transfer-safe lessons")
    transfer.add_argument("--output", required=True)
    ingest = sub.add_parser("knowledge-import", help="Import as proposals requiring local independent review")
    ingest.add_argument("--file", required=True)
    ingest.add_argument("--actor", required=True)
    check = sub.add_parser("check", help="Execute an authorized verification command without a shell")
    check.add_argument("--id", required=True)
    check.add_argument("--actor", required=True)
    check.add_argument("--token", required=True)
    check.add_argument("--argv", required=True, help="JSON file containing command argument array")
    args = parser.parse_args()
    try:
        ledger = Ledger(args.project)
        if args.command == "init":
            result = ledger.init(args.brief, read_json(args.config) if args.config else None)
        elif args.command == "request":
            result = ledger.apply(read_json(args.file))
        elif args.command == "check":
            result = ledger.check(args.id, args.actor, args.token, read_json(args.argv))
        elif args.command == "knowledge":
            result = ledger.knowledge(args.query, args.scope)
        elif args.command == "knowledge-export":
            result = ledger.transfer(args.output)
        elif args.command == "knowledge-import":
            result = ledger.import_lessons(args.file, args.actor)
        elif args.command == "status":
            result = ledger.status()
            if not args.full:
                fields = ("project_id", "status", "revision", "config", "claims", "checks_used", "research_used", "experiments_used", "brief_changed", "stale_artifacts", "reported_cost_usd", "cost_scope", "metrics")
                result = {k: result[k] for k in fields} | {"tasks": {k: {"status": t["status"], "stage": t["stage"], "depends_on": t["depends_on"], "rounds": t["rounds"]} for k, t in result["tasks"].items()}}
        else:
            result = getattr(ledger, args.command)()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not isinstance(result, dict) or result.get("passed") is not False else 1
    except (TeamError, KeyError, TypeError, OSError, json.JSONDecodeError, sqlite3.Error) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
