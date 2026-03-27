from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from build_scripts.utils import FileManager, SubtitleProcessor


VALIDATION_FALSE_MARKER = "validation function returned false"


def _relay_output(output: str) -> None:
    if output:
        print(output, end="" if output.endswith(("\n", "\r")) else "\n")


def run_templater(work_folder: Path, input_path: Path) -> None:
    aegisub_cli = work_folder / "aegisub-cli" / "aegisub-cli.exe"
    automation = work_folder / "aegisub-cli" / "automation" / "autoload" / "0x.KaraTemplater.moon"
    command = [str(aegisub_cli), "--automation", str(automation), str(input_path), str(input_path), "0x539's Templater"]
    if os.name != "nt":
        command = ["wine", *command]
    result = subprocess.run(command, check=False, capture_output=True, text=True, errors="replace")
    _relay_output(result.stdout)
    _relay_output(result.stderr)
    if result.returncode == 0:
        return

    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if VALIDATION_FALSE_MARKER in combined_output.lower():
        print(f"Skipping templater for {input_path}: validation returned false")
        return

    raise subprocess.CalledProcessError(
        result.returncode,
        result.args,
        output=result.stdout,
        stderr=result.stderr,
    )


def main(work_folder: str, line: str = "preview", version: str = "local-dev") -> None:
    work_dir = Path(work_folder).resolve()
    build_dir = work_dir / "build"

    FileManager.traverse_files(work_dir, line=line)

    for input_path in FileManager.iter_build_ass_files(build_dir):
        print(f"Running templates on {input_path}")
        run_templater(work_dir, input_path)

    for input_path in FileManager.iter_main_files(build_dir, line=line):
        output_path = build_dir / "output" / input_path.name
        current_dir = Path.cwd()
        try:
            os.chdir(input_path.parent)
            FileManager.merge_files(input_path, output_path)
        finally:
            os.chdir(current_dir)
        SubtitleProcessor.replace_version_placeholder(output_path, version)
        print(f"Merged {input_path.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("work_folder", help="Subtitle repository root")
    parser.add_argument("--line", default="preview", help="Build line: preview/tv/bd/movie")
    parser.add_argument("--version", default="local-dev", help="Version string for ${version}")
    arguments = parser.parse_args()

    main(arguments.work_folder, line=arguments.line, version=arguments.version)
