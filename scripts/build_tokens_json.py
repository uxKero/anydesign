#!/usr/bin/env python3
"""
build_tokens_json.py — Derive design-tokens.json (W3C DTCG) from a design.md

The design.md frontmatter already holds the token map, and its Section 2 tables
already hold each token's role and confidence. Writing design-tokens.json by
hand repeats all of that as output tokens; this script builds it instead.

What it reads:
- Frontmatter groups: colors, typography, spacing, rounded, and optionally
  shadows / elevation / motion (any flat map of name: value).
- Markdown tables whose first cell is a `token` in backticks: the Role or Use
  column becomes $description, the Confidence column (or a ✅/⚠️/❓ cell)
  becomes $extensions.anydesign.confidence.

Output shape matches what export_for_claude_design.py consumes: color.*,
typography.font-family / font-size / font-weight / line-height / letter-spacing,
spacing.*, radius.*, shadow.*, motion.*.

Usage:
    python build_tokens_json.py design.md
    python build_tokens_json.py design.md --output ./design-tokens.json

Stdlib only (uses PyYAML when installed, otherwise a small built-in parser that
covers the frontmatter shape the template defines).
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
CONFIDENCE_WORDS = (("✅", "high"), ("⚠", "medium"), ("❓", "low"),
                    ("high", "high"), ("medium", "medium"), ("low", "low"))


def parse_scalar(raw):
    raw = raw.strip()
    if not raw:
        return None
    if raw[0] in "\"'" and raw[-1] == raw[0] and len(raw) > 1:
        return raw[1:-1]
    if raw.startswith("[") and raw.endswith("]"):
        return [parse_scalar(x) for x in split_inline_list(raw[1:-1]) if x.strip()]
    if raw.startswith("{") and raw.endswith("}"):
        pairs = (item.split(":", 1) for item in split_inline_list(raw[1:-1]) if ":" in item)
        return {k.strip().strip("\"'"): parse_scalar(v) for k, v in pairs}
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    return raw


def split_inline_list(text):
    items, depth, quote, current = [], 0, None, ""
    for ch in text:
        if quote:
            current += ch
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "[({":
            depth += 1
        elif ch in "])}":
            depth -= 1
        elif ch == "," and depth == 0:
            items.append(current)
            current = ""
            continue
        current += ch
    items.append(current)
    return items


def strip_comment(line):
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line.rstrip()


def mini_yaml(text):
    root = {}
    stack = [(-1, root)]
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        line = strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        m = re.match(r"^\s*([^:]+?)\s*:(?:\s+(.*))?$", line)
        if not m:
            continue
        key, value = m.group(1).strip().strip("\"'"), (m.group(2) or "").strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value in ("|", ">", "|-", ">-"):
            block = []
            while i < len(lines) and (not lines[i].strip() or
                                      len(lines[i]) - len(lines[i].lstrip()) > indent):
                block.append(lines[i].strip())
                i += 1
            parent[key] = ("\n" if value.startswith("|") else " ").join(block).strip()
        elif value == "":
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            parent[key] = parse_scalar(value)
    return root


def load_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    try:
        import yaml
        data = yaml.safe_load(m.group(1))
    except ImportError:
        data = mini_yaml(m.group(1))
    return data or {}, text[m.end():]


def table_metadata(body):
    meta = {}
    header = None
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        name = re.fullmatch(r"`\{?([^`{}]+)\}?`", cells[0]) if cells else None
        if not name:
            continue
        entry, hex_value = {}, None
        for col, cell in zip(header, cells):
            if col in ("role", "use", "usage", "purpose") and cell:
                entry["description"] = cell
            found = re.search(r"#[0-9a-fA-F]{3,8}", cell)
            if col in ("hex", "value") and found:
                hex_value = found.group(0).lower()
            if col == "confidence" or any(sym in cell for sym in ("✅", "⚠", "❓")):
                for needle, level in CONFIDENCE_WORDS:
                    if needle in cell.lower() or needle in cell:
                        entry["confidence"] = level
                        break
        key = name.group(1).split(".")[-1].lstrip("-")
        meta.setdefault(key, {}).update(entry)
        if hex_value:
            meta.setdefault(hex_value, {}).update(entry)
    return meta


def leaf(value, ttype, name, meta, source):
    node = {"$value": value, "$type": ttype}
    info = meta.get(name) or (meta.get(value.lower(), {}) if isinstance(value, str) else {})
    if info.get("description"):
        node["$description"] = info["description"]
    ext = {"source": source}
    if info.get("confidence"):
        ext["confidence"] = info["confidence"]
    node["$extensions"] = {"anydesign": ext}
    return node


def dimension_type(value):
    return "dimension" if isinstance(value, str) and re.search(r"\d(px|rem|em|%)$", value) else "number"


def build(fm, meta):
    source = "design.md frontmatter"
    out = {}

    colors = fm.get("colors") or {}
    if colors:
        out["color"] = {n: leaf(v, "color", n, meta, source) for n, v in colors.items()}

    typography = fm.get("typography") or {}
    if typography:
        groups = {"font-family": {}, "font-size": {}, "font-weight": {},
                  "line-height": {}, "letter-spacing": {}}
        families = {}
        for style, spec in typography.items():
            if not isinstance(spec, dict):
                continue
            family = spec.get("fontFamily")
            if family and family not in families:
                families[family] = style
                groups["font-family"][style] = leaf(family, "fontFamily", style, meta, source)
            if "fontSize" in spec:
                groups["font-size"][style] = leaf(spec["fontSize"], "dimension", style, meta, source)
            if "fontWeight" in spec:
                groups["font-weight"][style] = leaf(spec["fontWeight"], "fontWeight", style, meta, source)
            if "lineHeight" in spec:
                groups["line-height"][style] = leaf(spec["lineHeight"], dimension_type(spec["lineHeight"]),
                                                    style, meta, source)
            if "letterSpacing" in spec:
                groups["letter-spacing"][style] = leaf(spec["letterSpacing"], "dimension", style, meta, source)
        out["typography"] = {k: v for k, v in groups.items() if v}

    spacing = fm.get("spacing") or {}
    if spacing:
        node = {}
        base = spacing.get("base")
        unit = "px"
        if isinstance(base, str):
            m = re.match(r"^[\d.]+([a-z%]+)$", base)
            unit = m.group(1) if m else unit
            node["base"] = leaf(base, "dimension", "base", meta, source)
        for step in spacing.get("scale") or []:
            value = step if isinstance(step, str) else f"{step}{unit}"
            node[str(step).replace(unit, "")] = leaf(value, "dimension", str(step), meta, source)
        for name, value in spacing.items():
            if name not in ("base", "scale") and not isinstance(value, (dict, list)):
                node[name] = leaf(value, "dimension", name, meta, source)
        out["spacing"] = node

    for key, group, ttype in (("rounded", "radius", "dimension"), ("radius", "radius", "dimension"),
                              ("shadows", "shadow", "shadow"), ("shadow", "shadow", "shadow"),
                              ("elevation", "shadow", "shadow"), ("motion", "motion", "duration")):
        values = fm.get(key) or {}
        if isinstance(values, dict) and values:
            out.setdefault(group, {}).update(
                {n: leaf(v, ttype, n, meta, source) for n, v in values.items() if not isinstance(v, dict)}
            )

    out["$extensions"] = {
        "anydesign": {
            "source": fm.get("source"),
            "captured_at": str(fm.get("captured_at")) if fm.get("captured_at") else None,
            "method": "generated from design.md by scripts/build_tokens_json.py",
            "spec": "W3C Design Tokens Community Group 2025.10",
        }
    }
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Build design-tokens.json (DTCG) from a design.md. Stdlib only.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("design_md", help="Path to the design.md")
    parser.add_argument("--output", "-o", default=None,
                        help="Output path (default: design-tokens.json next to the design.md)")
    args = parser.parse_args()

    path = Path(args.design_md)
    fm, body = load_frontmatter(path.read_text(encoding="utf-8"))
    if fm is None:
        print(f"No YAML frontmatter found in {path}", file=sys.stderr)
        sys.exit(1)

    tokens = build(fm, table_metadata(body))
    out_path = Path(args.output) if args.output else path.with_name("design-tokens.json")
    out_path.write_text(json.dumps(tokens, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    counts = {k: sum(1 for _ in walk(v)) for k, v in tokens.items() if not k.startswith("$")}
    with_conf = sum(1 for k, v in tokens.items() if not k.startswith("$")
                    for node in walk(v) if "confidence" in node["$extensions"]["anydesign"])
    total = sum(counts.values())
    print(f"Wrote {total} tokens to {out_path}: " + ", ".join(f"{k} {n}" for k, n in counts.items())
          + f". {with_conf} carry a confidence from the design.md tables.")


def walk(tree):
    for key, val in tree.items():
        if key.startswith("$"):
            continue
        if isinstance(val, dict) and "$value" in val:
            yield val
        elif isinstance(val, dict):
            yield from walk(val)


if __name__ == "__main__":
    main()
