"""Install the portable toolkit and native integration without overwriting user changes."""
import argparse
import shutil
from pathlib import Path


def plan_install(target):
    source = Path(__file__).resolve().parent
    target = Path(target).resolve()
    if not target.is_dir():
        raise ValueError("Target repository directory must already exist")
    if target.is_relative_to(source):
        raise ValueError("Choose the target repository, not the toolkit itself or one of its subdirectories")
    pairs = []
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(source)
        if any(p in {"__pycache__", ".startup-team", ".git", ".runtime"} for p in rel.parts):
            continue
        destinations = [target / "tools" / "startup-team" / rel]
        if rel.parts[0] in {".agents", ".codex"}:
            destinations.append(target / rel)
        for dest in destinations:
            dest = dest.resolve()
            if not dest.is_relative_to(target):
                raise ValueError(f"Destination resolves outside target: {dest}")
            if dest == path.resolve():
                continue
            if dest.exists():
                if not dest.is_file() or dest.read_bytes() != path.read_bytes():
                    raise ValueError(f"Existing file differs; no files installed: {dest}")
            else:
                pairs.append((path, dest))
    return pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        pairs = plan_install(args.target)
        for _, dest in pairs:
            print(dest)
        if args.check:
            print(f"Preflight passed: {len(pairs)} new files; nothing written.")
            return 0
        for source, dest in pairs:
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation refuses a file that appeared after preflight.
            with source.open("rb") as src, dest.open("xb") as out:
                shutil.copyfileobj(src, out)
        print(f"Installed {len(pairs)} files. Open a fresh Codex chat and select $startup-team.")
        return 0
    except (ValueError, OSError) as error:
        print(f"Installation stopped: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
