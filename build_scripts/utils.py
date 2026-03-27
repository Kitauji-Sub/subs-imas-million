from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import ass
import requests
import subdigest
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

from build_scripts import config


class CallbackRetry(Retry):
    def __init__(self, *args, **kwargs):
        self._callback = kwargs.pop("callback", None)
        super().__init__(*args, **kwargs)

    def new(self, **kwargs):
        kwargs["callback"] = self._callback
        return super().new(**kwargs)

    def increment(self, method=None, url=None, *args, **kwargs):
        if self._callback:
            try:
                self._callback(url)
            except Exception:
                print("Retry callback raised an exception, ignoring")
        return super().increment(method=method, url=url, *args, **kwargs)


class SubtitleProcessor:
    def __init__(self, input_file: Path, output_file: Path):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)

    @staticmethod
    def replace_fonts(text: str, replacements: dict[str, str]) -> str:
        for old_font, new_font in replacements.items():
            text = text.replace(old_font, new_font)
        return text

    def cleanup_ass_file(self) -> None:
        with self.input_file.open(encoding="utf-8-sig", mode="r") as handle:
            print(f"Cleaning file {self.input_file} ...")
            subtitles = subdigest.Subtitles(ass.parse(handle), "s")
            subtitles.selection_set("effect", "fx").remove_selected()

            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            with self.output_file.open(encoding="utf-8-sig", mode="w+") as output:
                subtitles.dump_file(output)

    def traditionalize_text(
        self,
        input_text: str,
        user_pre_replace: str = "",
        user_protect_replace: str = "",
        timeout: int = 10,
        max_tries: int = 5,
    ) -> str:
        def retry_callback(url: str | None) -> None:
            print(f"Retrying for {url}...")

        session = requests.Session()
        retry = CallbackRetry(
            total=max_tries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 504],
            respect_retry_after_header=True,
            callback=retry_callback,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)

        try:
            response = session.post(
                "https://api.zhconvert.org/convert",
                data={
                    "text": input_text,
                    "converter": "Taiwan",
                    "userPreReplace": user_pre_replace,
                    "userProtectReplace": user_protect_replace,
                },
                timeout=timeout,
            )
            response.raise_for_status()
            result = response.json()
            if "data" in result and "text" in result["data"]:
                return result["data"]["text"]
            raise RuntimeError("Unexpected response format from zhconvert")
        except RequestException as error:
            raise RuntimeError("Maximum number of retries exceeded while calling zhconvert") from error

    def traditionalize_ass(
        self,
        user_pre_replace: str = "",
        user_protect_replace: str = "",
    ) -> None:
        with self.input_file.open(encoding="utf-8-sig", mode="r") as handle:
            document = ass.parse(handle)
            source_texts = [event.text for event in document.events]
            traditionalized: list[str] = []

            print(f"Traditionalizing {self.input_file}")
            for index in range(0, len(source_texts), 50):
                print(f"Traditionalizing line {index} to {index + 50}...")
                slice_texts = [
                    self.replace_fonts(text, config.FONT_REPLACEMENTS)
                    for text in source_texts[index : index + 50]
                ]
                payload = json.dumps(slice_texts, ensure_ascii=False)
                converted = self.traditionalize_text(
                    payload,
                    user_pre_replace=user_pre_replace,
                    user_protect_replace=user_protect_replace,
                )
                traditionalized.extend(json.loads(converted))

            for index, text in enumerate(traditionalized):
                document.events[index].text = text
                if document.events[index].effect.startswith("import"):
                    document.events[index].text = (
                        document.events[index]
                        .text.replace(".ass", "_tc.ass")
                        .replace("_sc_tc.ass", "_tc.ass")
                    )

            for style in document.styles:
                if style.fontname == "方正FW筑紫黑 简 E":
                    style.fontsize = "75"
                    style.bold = "-1"
                style.fontname = self.replace_fonts(style.fontname, config.FONT_REPLACEMENTS)

            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            with self.output_file.open(encoding="utf-8-sig", mode="w+") as output:
                document.dump_file(output)

    @staticmethod
    def replace_version_placeholder(file_path: Path, version: str) -> None:
        text = file_path.read_text(encoding="utf-8-sig")
        text = text.replace(config.VERSION_PLACEHOLDER, version)
        file_path.write_text(text, encoding="utf-8-sig")


class FileManager:
    @staticmethod
    def _skip_root(root: Path) -> bool:
        return any(part in config.SKIP_DIR_NAMES for part in root.parts)

    @staticmethod
    def _should_skip_for_line(path: Path, line: str) -> bool:
        if line == "movie":
            return "Movies" not in path.parts
        return "Movies" in path.parts

    @staticmethod
    def _should_copy_directly(path: Path) -> bool:
        return path.name.startswith(("op", "ed"))

    @staticmethod
    def iter_source_files(work_folder: Path, line: str):
        for root, dirs, files in os.walk(work_folder):
            root_path = Path(root)
            dirs[:] = [
                directory
                for directory in dirs
                if directory not in config.SKIP_DIR_NAMES
            ]

            if FileManager._skip_root(root_path):
                continue
            if FileManager._should_skip_for_line(root_path, line):
                continue

            for file_name in sorted(files):
                path = root_path / file_name
                if path.suffix != ".ass" or path.name.endswith("_tc.ass"):
                    continue
                yield path

    @staticmethod
    def traverse_files(work_folder: Path, line: str) -> None:
        build_dir = work_folder / "build"
        if build_dir.exists():
            print("Cleaning old build directory ...")
            shutil.rmtree(build_dir)

        for input_file in FileManager.iter_source_files(work_folder, line):
            output_file = build_dir / input_file.relative_to(work_folder)
            if input_file.name.endswith("_sc.ass"):
                output_tc_file = build_dir / (
                    input_file.relative_to(work_folder)
                    .with_suffix("")
                    .as_posix()
                    .replace("_sc", "_tc")
                )
                output_tc_file = output_tc_file.with_suffix(".ass")
            else:
                output_tc_file = build_dir / input_file.relative_to(work_folder).with_suffix("")
                output_tc_file = output_tc_file.with_name(output_tc_file.name + "_tc.ass")

            print(f"Preprocessing {input_file} ...")
            if FileManager._should_copy_directly(input_file):
                output_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(input_file, output_file)
                tc_source = input_file.with_name(input_file.name.replace("_sc.ass", "_tc.ass"))
                if tc_source.exists():
                    shutil.copy2(tc_source, output_file.with_name(output_file.name.replace("_sc.ass", "_tc.ass")))
                continue

            processor = SubtitleProcessor(input_file, output_file)
            processor.cleanup_ass_file()

            processor_tc = SubtitleProcessor(output_file, output_tc_file)
            processor_tc.traditionalize_ass(
                user_pre_replace=config.USER_PRE_REPLACE,
                user_protect_replace=config.USER_PROTECT_REPLACE,
            )

    @staticmethod
    def iter_build_ass_files(build_dir: Path):
        for path in sorted(build_dir.rglob("*.ass")):
            if "output" in path.parts:
                continue
            yield path

    @staticmethod
    def iter_main_files(build_dir: Path, line: str):
        if line == "movie":
            patterns = ("act",)
        else:
            patterns = ("ep", "ova")

        for path in FileManager.iter_build_ass_files(build_dir):
            if not path.name.endswith(".ass"):
                continue
            if not path.name.endswith(("_sc.ass", "_tc.ass")):
                continue
            if path.parent.name in {"insert", "screen", "staff"}:
                continue
            if path.name.startswith(patterns):
                yield path

    @staticmethod
    def merge_files(input_file: Path, output_file: Path) -> None:
        with input_file.open(encoding="utf-8-sig", mode="r") as handle:
            subtitles = subdigest.Subtitles(ass.parse(handle), "s")
            subtitles.ms_import_rc()

            output_file.parent.mkdir(parents=True, exist_ok=True)
            with output_file.open(encoding="utf-8-sig", mode="w+") as output:
                subtitles.dump_file(output)
