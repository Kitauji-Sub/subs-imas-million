from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_scripts import config  # noqa: E402


TEXT_START_RE = re.compile(r"=====TEXT(?: CN| SC)?=====")
TEXT_JP_RE = re.compile(r"=====TEXT JP=====")
TOP_ALIGN_RE = re.compile(r"\\an([789])")
POSITIONING_RE = re.compile(r"\\(?:pos|move|clip|iclip|org|p\d+)")
STYLE_RESET_RE = re.compile(r"\\r([^\\}]+?)(?=\\|})")
LEADING_BLOCK_RE = re.compile(r"^\{([^}]*)\}")

JP_STRIP_PATTERNS = [
    re.compile(r"\\fn[^\\}]+"),
    re.compile(r"\\fs-?\d+(?:\.\d+)?"),
    re.compile(r"\\bord-?\d+(?:\.\d+)?"),
    re.compile(r"\\blur-?\d+(?:\.\d+)?"),
    re.compile(r"\\fscx-?\d+(?:\.\d+)?"),
    re.compile(r"\\fscy-?\d+(?:\.\d+)?"),
    re.compile(r"\\fsp-?\d+(?:\.\d+)?"),
]


@dataclass
class Event:
    kind: str
    layer: str
    start: str
    end: str
    style: str
    name: str
    margin_l: str
    margin_r: str
    margin_v: str
    effect: str
    text: str

    def signature(self, top_style: str) -> tuple[str, ...]:
        speaker = self.style if self.style in config.SPEAKER_COLORS else ""
        identity = speaker or self.style
        preserved_name = "" if speaker else self.name
        return (
            self.start,
            self.end,
            identity,
            preserved_name,
            self.margin_l,
            self.margin_r,
            top_style,
        )


def parse_event(line: str) -> Event:
    kind, payload = line.split(": ", 1)
    row = payload.split(",", 9)
    while len(row) < 10:
        row.append("")
    return Event(kind=kind, layer=row[0], start=row[1], end=row[2], style=row[3], name=row[4], margin_l=row[5], margin_r=row[6], margin_v=row[7], effect=row[8], text=row[9])


def serialize_event(event: Event) -> str:
    return (
        f"{event.kind}: "
        f"{event.layer},{event.start},{event.end},{event.style},{event.name},"
        f"{event.margin_l},{event.margin_r},{event.margin_v},{event.effect},{event.text}"
    )


def parse_timestamp(timestamp: str) -> int:
    hours, minutes, seconds = timestamp.split(":")
    second, centisecond = seconds.split(".")
    return (
        int(hours) * 60 * 60 * 1000
        + int(minutes) * 60 * 1000
        + int(second) * 1000
        + int(centisecond) * 10
    )


def detect_text_ranges(events: list[Event]) -> tuple[int, int, int] | None:
    text_start = next((index for index, event in enumerate(events) if TEXT_START_RE.search(event.text)), None)
    text_jp = next((index for index, event in enumerate(events) if TEXT_JP_RE.search(event.text)), None)
    import_start = next((index for index, event in enumerate(events) if event.effect.startswith("import")), len(events))
    if text_start is None or text_jp is None:
        return None
    return text_start, text_jp, import_start


def choose_generic_style(text: str) -> str:
    return "Text_Top" if TOP_ALIGN_RE.search(text) else "Text_Bottom"


def inline_color_tags(style_name: str) -> str:
    colors = config.SPEAKER_COLORS.get(style_name)
    if not colors:
        return ""
    return f"\\3c{colors['outline']}\\4c{colors['shadow']}"


def replace_style_resets(text: str, generic_style: str) -> str:
    def repl(match: re.Match[str]) -> str:
        style_name = match.group(1).strip()
        if style_name in {"Text_Bottom", "Text_Top", "其它"}:
            return f"\\r{generic_style}"
        if style_name in config.SPEAKER_COLORS:
            return f"\\r{generic_style}{inline_color_tags(style_name)}"
        return f"\\r{generic_style}"

    return STYLE_RESET_RE.sub(repl, text)


def strip_leading_tags(text: str, strip_jp_style: bool) -> str:
    while True:
        match = LEADING_BLOCK_RE.match(text)
        if not match:
            return text
        block = match.group(1)
        new_block = TOP_ALIGN_RE.sub("", block)
        if strip_jp_style:
            for pattern in JP_STRIP_PATTERNS:
                new_block = pattern.sub("", new_block)
        if new_block == block:
            return text
        text = text[match.end() :]
        if new_block.strip():
            text = "{" + new_block + "}" + text
            return text


def normalize_templated_text(text: str, generic_style: str, strip_jp_style: bool) -> str:
    text = replace_style_resets(text, generic_style)
    return strip_leading_tags(text, strip_jp_style=strip_jp_style)


def prepend_tags(text: str, tags: str) -> str:
    if not tags:
        return text
    return "{" + tags + "}" + text


def migrate_manual_line(event: Event, source: str) -> Event:
    if event.style in {"注释", "OnScreen", "Title", "Default"}:
        return event

    generic_style = choose_generic_style(event.text)
    speaker_key = event.style if event.style in config.SPEAKER_COLORS else ""
    strip_jp_style = source == "jp" and not POSITIONING_RE.search(event.text)
    text = normalize_templated_text(event.text, generic_style, strip_jp_style=strip_jp_style)
    if speaker_key:
        text = prepend_tags(text, inline_color_tags(speaker_key))

    return Event(
        kind=event.kind,
        layer=event.layer,
        start=event.start,
        end=event.end,
        style=generic_style,
        name=speaker_key or event.name,
        margin_l=event.margin_l,
        margin_r=event.margin_r,
        # Legacy per-line 70/80 MarginV values existed to dodge the separate JP row.
        # Once SC/JP are merged into one templated source line, fall back to style defaults.
        margin_v="0",
        effect=event.effect,
        text=text,
    )


def migrate_kara_line(event: Event, partner_text: str | None = None, jp_only: bool = False) -> Event:
    generic_style = choose_generic_style(event.text if not jp_only else partner_text or "")
    speaker_key = event.style if event.style in config.SPEAKER_COLORS else ""
    sc_text = "" if jp_only else normalize_templated_text(event.text, generic_style, strip_jp_style=False)
    jp_text = partner_text or ""
    if jp_text:
        jp_text = normalize_templated_text(jp_text, generic_style, strip_jp_style=True)

    merged_text = sc_text
    if jp_text:
        merged_text = f"{sc_text}\\N{jp_text}" if sc_text else f"\\N{jp_text}"

    return Event(
        kind="Comment",
        layer="0",
        start=event.start,
        end=event.end,
        style=generic_style,
        name=speaker_key or event.name,
        margin_l=event.margin_l,
        margin_r=event.margin_r,
        # Old 70/80 MarginV values only existed to separate standalone JP rows.
        # After merging into a single bilingual source line, let the generic style decide.
        margin_v="0",
        effect="kara",
        text=merged_text,
    )


def is_pairable(event: Event) -> bool:
    return (
        event.kind == "Dialogue"
        and not event.effect.startswith("import")
        and event.style not in {"注释", "OnScreen", "Title", "Default"}
        and not POSITIONING_RE.search(event.text)
    )


def build_speaker_color_line() -> str:
    entries = ",".join(
        f'["{name}"]={{outline="{colors["outline"]}",shadow="{colors["shadow"]}"}}'
        for name, colors in sorted(config.SPEAKER_COLORS.items())
    )
    return (
        "Comment: 0,0:00:00.00,0:00:00.00,Text_Bottom,speaker_color,0,0,0,code once style Text_Bottom style Text_Top,"
        f"speaker_color = {{{entries}}}; function speaker_tags(key) local colors = speaker_color[key]; if not colors then return \"\" end; return string.format(\"\\\\3c%s\\\\4c%s\", colors.outline, colors.shadow) end"
    )


def template_block() -> list[str]:
    return [
        "Comment: 0,0:00:00.00,0:00:00.00,Text_Bottom,settings,0,0,0,code once style Text_Bottom style Text_Top,_zh_jp_gap = 50; _zh_jp_gap_top = 50; jp_font_name = \"FOT-TsukuGo Pro E\"; jp_scale = 92; ruby_scale = 60; ruby_gap = 10; reverse_top = true;",
        build_speaker_color_line(),
        "Comment: 0,0:00:00.00,0:00:00.00,Text_Bottom,utils,0,0,0,code once style Text_Bottom style Text_Top,local re = require('re') local function safe_text_extents(style, text) if aegisub and aegisub.text_extents then return aegisub.text_extents(style, text) else return 0, 0, 0, 0 end end local function gmatch(str, pattern) local matches = {} for match, start_idx, end_idx in re.gfind(str, pattern) do local groups = re.match(match, pattern) if not groups then groups = {} end for i = 1, #groups do groups[i]['first'] = groups[i]['first'] + start_idx - 1 groups[i]['last'] = groups[i]['last'] + start_idx - 1 end table.insert(matches, groups) end return matches end function remove_tags(text) if not text then return '' end return re.sub(text, '\\\\{[^}]*\\\\}', '', 0) end local function extract_rubys(text, style) local rubys = {} if not text then return rubys end local original_text = text for _, ruby_match in _G.ipairs(gmatch(original_text, '\\\\{ruby=([^}]+)\\\\}([^{]*?)\\\\{/ruby\\\\}')) do local ruby_text = ruby_match[2].str local annotated_text = ruby_match[3].str local before_text = string.sub(original_text, 1, ruby_match[1].first - 1) local clean_before_text = remove_tags(before_text) local clean_annotated_text = remove_tags(annotated_text) local annotated_width = 0 if clean_annotated_text ~= '' then local width = safe_text_extents(style, clean_annotated_text) annotated_width = width or 0 end local before_width = 0 if clean_before_text ~= '' then local width = safe_text_extents(style, clean_before_text) before_width = width or 0 end table.insert(rubys, { text = ruby_text, pos = before_width + annotated_width / 2 }) end return rubys end function process_bilingual_subtitle(raw_text, style) if not raw_text or raw_text == '' then return { text = '', width = 0, height = 0 }, { text = '', width = 0, height = 0 }, {} end local parts = re.split(raw_text, '\\\\\\\\N') local chinese_text = parts[1] or '' local japanese_text = parts[2] or '' local rubys = extract_rubys(chinese_text, style) local chinese_clean = remove_tags(chinese_text) chinese_clean = re.sub(chinese_clean, '\\\\{ruby=[^}]+\\\\}([^{]*?)\\\\{/ruby\\\\}', '%1', 0) local chinese_width, chinese_height = 0, 0 if chinese_clean ~= '' then local width, height = safe_text_extents(style, chinese_clean) chinese_width = width or 0 chinese_height = height or 0 end local japanese_clean = remove_tags(japanese_text) local japanese_width, japanese_height = 0, 0 if japanese_clean ~= '' then local width, height = safe_text_extents(style, japanese_clean) japanese_width = width or 0 japanese_height = height or 0 end return { text = chinese_text, width = chinese_width, height = chinese_height }, { text = japanese_text, width = japanese_width, height = japanese_height }, rubys end",
        "Comment: 0,0:00:00.00,0:00:00.00,Text_Bottom,gv,0,0,0,code line style Text_Bottom style Text_Top,chinese, japanese, rubys = process_bilingual_subtitle(orgline.text, orgline.styleref); has_chinese = chinese ~= nil and chinese.text ~= ''; has_japanese = japanese ~= nil and japanese.text ~= ''; has_ruby = false; if rubys then for _, ruby in _G.ipairs(rubys) do has_ruby = true end end; zh_jp_gap = has_japanese and _zh_jp_gap or 0; zh_jp_gap_top = has_japanese and _zh_jp_gap_top or 0; base_width = has_chinese and chinese.width or japanese.width; line_left = (meta.res_x - orgline.eff_margin_l - orgline.eff_margin_r - base_width) / 2 + orgline.eff_margin_l; is_top = orgline.styleref.align == 8; speaker_tag = speaker_tags(orgline.actor); local c_pos_x, c_pos_y, j_pos_x, j_pos_y, ruby_pos_y if is_top then if reverse_top then if has_ruby then c_pos_x, c_pos_y = orgline.center, (orgline.top + ruby_gap + (chinese.height * ruby_scale / 100)) j_pos_x, j_pos_y = orgline.center, (orgline.top + ruby_gap + (chinese.height * ruby_scale / 100) + zh_jp_gap_top) ruby_pos_y = orgline.top else c_pos_x, c_pos_y = orgline.center, orgline.top j_pos_x, j_pos_y = orgline.center, (orgline.top + zh_jp_gap_top) ruby_pos_y = 0 end else c_pos_x, c_pos_y = orgline.center, (orgline.top + zh_jp_gap_top) j_pos_x, j_pos_y = orgline.center, orgline.top ruby_pos_y = orgline.bottom + zh_jp_gap_top + ruby_gap end else c_pos_x, c_pos_y = orgline.center, (orgline.bottom - zh_jp_gap) j_pos_x, j_pos_y = orgline.center, orgline.bottom ruby_pos_y = orgline.top - zh_jp_gap - ruby_gap end chinese_pos_tag = [[\\pos(]] .. c_pos_x .. [[,]] .. c_pos_y .. [[)]] japanese_pos_tag = [[\\pos(]] .. j_pos_x .. [[,]] .. j_pos_y .. [[)]] ruby_y = ruby_pos_y",
        "Comment: 0,0:00:00.00,0:00:00.00,Text_Bottom,,0,0,0,template line style Text_Bottom style Text_Top notext if has_chinese,!relayer(9)!{!chinese_pos_tag!!speaker_tag!}!chinese.text!",
        "Comment: 0,0:00:00.00,0:00:00.00,Text_Bottom,,0,0,0,template line style Text_Bottom style Text_Top notext if has_japanese,!relayer(8)!{!japanese_pos_tag!\\fscx!jp_scale!\\fscy!jp_scale!\\fn!jp_font_name!!speaker_tag!}!japanese.text!",
        "Comment: 0,0:00:00.00,0:00:00.00,Text_Bottom,,0,0,0,template line style Text_Bottom style Text_Top notext if has_ruby,!relayer(9)!{!maxloop(\"ruby\", #rubys)!\\pos(!line_left + rubys[loopctx.state.ruby].pos!,!ruby_y!)\\fscx!ruby_scale!\\fscy!ruby_scale!\\bord!line.styleref.outline * 0.8!!speaker_tag!}!rubys[loopctx.state.ruby].text!",
    ]


def transform_events(events: list[Event]) -> list[Event] | None:
    ranges = detect_text_ranges(events)
    if not ranges:
        return None

    text_start, text_jp, import_start = ranges
    prefix = events[:text_start]
    sc_events = events[text_start + 1 : text_jp]
    jp_events = events[text_jp + 1 : import_start]
    suffix = events[import_start:]

    jp_lookup: dict[tuple[str, ...], deque[int]] = defaultdict(deque)
    for index, event in enumerate(jp_events):
        if is_pairable(event):
            jp_lookup[event.signature(choose_generic_style(event.text))].append(index)

    migrated: list[tuple[tuple[int, int], Event]] = []
    used_jp: set[int] = set()

    for index, event in enumerate(sc_events):
        order_key = (parse_timestamp(event.start), index)
        if is_pairable(event):
            signature = event.signature(choose_generic_style(event.text))
            partner_index = None
            queue = jp_lookup.get(signature)
            while queue:
                candidate = queue.popleft()
                if candidate not in used_jp:
                    partner_index = candidate
                    used_jp.add(candidate)
                    break
            if partner_index is not None:
                migrated.append((order_key, migrate_kara_line(event, partner_text=jp_events[partner_index].text)))
            else:
                migrated.append((order_key, migrate_kara_line(event)))
        else:
            migrated.append((order_key, migrate_manual_line(event, source="sc")))

    base_order = len(sc_events) + 10
    for index, event in enumerate(jp_events):
        if index in used_jp:
            continue
        order_key = (parse_timestamp(event.start), base_order + index)
        if is_pairable(event):
            migrated.append((order_key, migrate_kara_line(event, partner_text=event.text, jp_only=True)))
        else:
            migrated.append((order_key, migrate_manual_line(event, source="jp")))

    migrated.sort(key=lambda item: item[0])
    text_marker = Event(
        kind="Comment",
        layer="0",
        start="0:00:00.00",
        end="0:00:00.00",
        style="注释",
        name="",
        margin_l="0",
        margin_r="0",
        margin_v="0",
        effect="",
        text="=====TEXT=====",
    )
    return prefix + [text_marker] + [event for _, event in migrated] + suffix


def migrate_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8-sig").splitlines()
    styles_header = original.index("[V4+ Styles]")
    style_format = styles_header + 1
    events_header = original.index("[Events]")
    event_format = events_header + 1
    post_event_index = next(
        (
            index
            for index in range(event_format + 1, len(original))
            if original[index].startswith("[")
        ),
        len(original),
    )
    event_lines = [line for line in original[event_format + 1 : post_event_index] if line.strip()]
    post_event_lines = original[post_event_index:]

    events = [parse_event(line) for line in event_lines]
    transformed = transform_events(events)
    if transformed is None:
        return False

    new_lines = []
    new_lines.extend(original[: style_format + 1])
    new_lines.extend(config.TEXT_GENERIC_STYLES)
    new_lines.extend(original[events_header : event_format + 1])
    new_lines.extend(template_block())
    new_lines.extend(serialize_event(event) for event in transformed)
    new_lines.extend(post_event_lines)

    with path.open("w", encoding="utf-8-sig", newline="\r\n") as handle:
        handle.write("\r\n".join(new_lines) + "\r\n")
    return True


def iter_target_files() -> list[Path]:
    return sorted(
        [path for path in ROOT.glob("ep*/ep*_sc.ass") if "Movies" not in path.parts]
        + [ROOT / "ova" / "ova_sc.ass"]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Only report files that need migration")
    args = parser.parse_args()

    changed = []
    for path in iter_target_files():
        if args.check:
            text = path.read_text(encoding="utf-8-sig")
            if "=====TEXT JP=====" in text:
                changed.append(path)
            continue
        if migrate_file(path):
            changed.append(path)

    for path in changed:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
