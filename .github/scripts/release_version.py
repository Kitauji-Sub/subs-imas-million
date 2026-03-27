from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SEMVER_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?(?P<fix>-fix)?$")


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    def bump(self, level: str) -> "Version":
        if level == "major":
            return Version(self.major + 1, 0, 0)
        if level == "minor":
            return Version(self.major, self.minor + 1, 0)
        return Version(self.major, self.minor, self.patch + 1)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def run_git(repo_root: Path, *args: str, check: bool = True) -> str:
    process = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=check,
        capture_output=True,
        text=True,
    )
    return process.stdout.strip()


def normalize_tag_version(tag: str, release_line: str) -> Version:
    suffix = tag.removeprefix(f"{release_line}-")
    match = SEMVER_RE.match(suffix)
    if not match:
        raise ValueError(f"Unsupported legacy tag format: {tag}")

    patch = int(match.group("patch") or 0)
    if match.group("fix"):
        patch += 1
    return Version(int(match.group("major")), int(match.group("minor")), patch)


def find_previous_tag(repo_root: Path, release_line: str) -> str:
    try:
        return run_git(repo_root, "describe", "--tags", "--abbrev=0", "--match", f"{release_line}-*", "HEAD")
    except subprocess.CalledProcessError:
        matches = run_git(repo_root, "tag", "--list", f"{release_line}-*").splitlines()
        if not matches:
            return ""
        return max(matches, key=lambda tag: normalize_tag_version(tag, release_line))


def determine_bump(repo_root: Path, since_tag: str) -> str:
    revision_range = f"{since_tag}..HEAD" if since_tag else "HEAD"
    log_output = run_git(repo_root, "log", "--format=%B%x00", revision_range)
    if not log_output:
        return "patch"

    messages = [message for message in log_output.split("\x00") if message.strip()]
    if any("(MAJOR)" in message for message in messages):
        return "major"
    if any("(MINOR)" in message for message in messages):
        return "minor"
    return "patch"


def build_preview_version(repo_root: Path) -> dict[str, str]:
    short_sha = run_git(repo_root, "rev-parse", "--short", "HEAD")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    version = f"latest-{timestamp}-{short_sha}"
    return {
        "version": version,
        "version_tag": "latest",
        "display_name": version,
        "release_line": "preview",
        "previous_tag": "latest",
        "bump": "preview",
    }


def build_stable_version(repo_root: Path, release_line: str) -> dict[str, str]:
    previous_tag = find_previous_tag(repo_root, release_line)
    base_version = normalize_tag_version(previous_tag, release_line) if previous_tag else Version(0, 0, 0)
    bump = determine_bump(repo_root, previous_tag)
    next_version = base_version.bump(bump)
    version_tag = f"{release_line}-{next_version}"
    return {
        "version": str(next_version),
        "version_tag": version_tag,
        "display_name": version_tag,
        "release_line": release_line,
        "previous_tag": previous_tag,
        "bump": bump,
    }


def write_outputs(path: str, outputs: dict[str, str]) -> None:
    with open(path, "a", encoding="utf-8") as handle:
        for key, value in outputs.items():
            handle.write(f"{key}={value}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices={"preview", "stable"}, required=True)
    parser.add_argument("--branch", help="Stable release branch name")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if args.mode == "preview":
        outputs = build_preview_version(repo_root)
    else:
        if not args.branch:
            raise SystemExit("--branch is required in stable mode")
        outputs = build_stable_version(repo_root, args.branch)

    for key, value in outputs.items():
        print(f"{key}={value}")

    if args.github_output:
        write_outputs(args.github_output, outputs)


if __name__ == "__main__":
    main()
