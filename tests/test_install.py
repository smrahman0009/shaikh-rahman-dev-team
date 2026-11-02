"""Portable installation checks; every write is inside a TemporaryDirectory."""
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import shutil
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch


BUNDLE = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        shutil.copytree(BUNDLE, self.source, ignore=shutil.ignore_patterns("__pycache__", ".runtime", ".startup-team", ".git"))
        self.target = self.root / "target"
        self.target.mkdir()
        self.installer = load("test_installer", self.source / "install.py")
        self.validator = load("test_validator", self.source / "validate_bundle.py")

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def run_install(self, check=False):
        output = io.StringIO()
        argv = ["install.py", "--target", str(self.target)] + (["--check"] if check else [])
        with patch.object(sys, "argv", argv), redirect_stdout(output):
            result = self.installer.main()
        return result, output.getvalue()

    def test_portable_placement_and_repeat_install_is_idempotent(self):
        before = self.snapshot(self.source)
        sentinel = self.root / "outside.txt"
        sentinel.write_text("untouched", encoding="utf-8")
        self.assertEqual(0, self.run_install()[0])
        installed = self.snapshot(self.target)
        for name, content in before.items():
            self.assertEqual(content, installed["tools/startup-team/" + name])
            if name.startswith((".agents/", ".codex/")):
                self.assertEqual(content, installed[name])
        expected = {"tools/startup-team/" + name for name in before}
        expected.update(name for name in before if name.startswith((".agents/", ".codex/")))
        self.assertEqual(expected, set(installed))
        self.assertEqual([], self.installer.plan_install(self.target))
        self.assertEqual(0, self.run_install()[0])
        self.assertEqual(installed, self.snapshot(self.target))
        self.assertEqual(before, self.snapshot(self.source))
        self.assertEqual("untouched", sentinel.read_text(encoding="utf-8"))
        self.assertEqual({"source", "target", "outside.txt"}, {p.name for p in self.root.iterdir()})

    def test_preflight_writes_nothing_and_conflict_never_partially_installs(self):
        self.assertEqual(0, self.run_install(check=True)[0])
        self.assertEqual([], list(self.target.iterdir()))
        conflict = self.target / ".agents/skills/startup-team/SKILL.md"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("User custom skill; preserve it", encoding="utf-8")
        before = self.snapshot(self.target)
        result, output = self.run_install()
        self.assertEqual(1, result)
        self.assertIn("Existing file differs", output)
        self.assertEqual(before, self.snapshot(self.target))
        self.assertFalse((self.target / "tools").exists())

    def test_private_runtime_and_git_data_are_excluded_at_every_depth(self):
        secret = ("private fixture " + self.temp.name).encode("utf-8")
        for directory in (".runtime", ".startup-team", ".git", "__pycache__", "nested/.runtime", "nested/.startup-team"):
            private = self.source / directory / "secret.txt"
            private.parent.mkdir(parents=True, exist_ok=True)
            private.write_bytes(secret)
        self.assertEqual(0, self.run_install()[0])
        installed = self.snapshot(self.target)
        self.assertFalse(any(secret in content for content in installed.values()))
        self.assertFalse(any(part in {".runtime", ".startup-team", ".git", "__pycache__"}
                             for name in installed for part in Path(name).parts))

    def test_destination_symlink_escape_is_rejected_without_outside_writes(self):
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (self.target / "tools").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Directory symlinks unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "outside target"):
            self.installer.plan_install(self.target)
        self.assertEqual(1, self.run_install()[0])
        self.assertEqual([], list(outside.iterdir()))
        self.assertEqual(["tools"], [p.name for p in self.target.iterdir()])

    def test_installed_skill_references_and_all_generated_roles_validate(self):
        self.assertEqual(0, self.run_install()[0])
        portable = self.target / "tools/startup-team"
        with redirect_stdout(io.StringIO()):
            self.validator.validate(portable)
        source_roles = {p.name for p in (self.source / ".codex/agents").glob("*.toml")}
        installed_roles = list((self.target / ".codex/agents").glob("*.toml"))
        self.assertEqual(source_roles, {p.name for p in installed_roles})
        self.assertGreaterEqual(len(installed_roles), 10)
        for path in installed_roles:
            with self.subTest(role=path.name):
                role = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(path.stem, role["name"])
                for field in ("description", "developer_instructions"):
                    self.assertTrue(role[field].strip())
        skill = self.target / ".agents/skills/startup-team"
        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertTrue((skill / "agents/openai.yaml").is_file())

    def test_validator_detects_broken_skill_reference(self):
        skill = self.source / ".agents/skills/startup-team/SKILL.md"
        with skill.open("a", encoding="utf-8") as out:
            out.write("\n[Missing reference](references/does-not-exist.md)\n")
        with self.assertRaisesRegex(AssertionError, "Broken link"):
            self.validator.validate(self.source)

    def test_validator_detects_missing_role_instructions(self):
        role = next((self.source / ".codex/agents").glob("*.toml"))
        role.write_text('name = "startup_invalid"\ndescription = "Missing required instructions"\n', encoding="utf-8")
        with self.assertRaises(AssertionError):
            self.validator.validate(self.source)


if __name__ == "__main__":
    unittest.main()
