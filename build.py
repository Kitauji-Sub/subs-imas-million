from __future__ import annotations

import argparse
import os

from build_scripts.build import main as build_main


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "work_folder",
        nargs="?",
        default=os.environ.get("GITHUB_WORKSPACE", os.getcwd()),
        help="Subtitle repository root",
    )
    parser.add_argument(
        "--line",
        default=os.environ.get("RELEASE_LINE", "preview"),
        help="Build line: preview/tv/bd/movie",
    )
    parser.add_argument(
        "--version",
        default=os.environ.get("SUB_VERSION", "local-dev"),
        help="Version string for ${version}",
    )
    arguments = parser.parse_args()

    build_main(arguments.work_folder, line=arguments.line, version=arguments.version)


if __name__ == "__main__":
    main()
