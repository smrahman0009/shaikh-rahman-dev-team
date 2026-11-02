"""Dependency-free structural validation for this toolkit (not a general YAML parser)."""
import re
import tomllib
from pathlib import Path


def validate(root=None):
    root = Path(root or Path(__file__).resolve().parent)
    skill = root / ".agents/skills/startup-team"
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), "Missing skill frontmatter"
    meta = text.split("---", 2)[1]
    assert re.search(r"^name: startup-team$", meta, re.M)
    assert re.search(r"^description: .+", meta, re.M)
    for path in skill.rglob("*.md"):
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" not in link and not link.startswith("#"):
                assert (path.parent / link.split("#")[0]).exists(), f"Broken link {path}: {link}"
    names = []
    for path in (root / ".codex/agents").glob("*.toml"):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        assert all(isinstance(data.get(k), str) and data[k].strip() for k in ("name", "description", "developer_instructions")), path
        assert data["name"].startswith("startup_"), path
        names.append(data["name"])
    assert len(names) >= 10 and len(set(names)) == len(names), "Missing or duplicate roles"
    assert (root / "team.py").is_file()
    print(f"Validated skill frontmatter, references, toolkit entrypoint and {len(names)} TOML agents.")


if __name__ == "__main__":
    validate()
