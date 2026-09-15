#!/usr/bin/env python3
"""
extract_css_vars.py — Extract CSS custom properties from a URL

Fetches the HTML of a URL, discovers every linked stylesheet and inline
<style> block, downloads them, and extracts all `--name: value;` definitions.
Groups them heuristically by category (color / spacing / typography / radius /
shadow / other), writes the full JSON document to disk and prints a compact
digest: numeric scales collapsed to one line, var() aliases resolved, framework
internals dropped, capped to a character budget. The digest is what the model
reads; the full JSON stays on disk and --grep searches it by name.

These are *explicit* design tokens — the ones the developer/designer named.
They should be marked as ✅ high confidence in the design.md output.

Stdlib only. No pip install required.

Usage:
    python extract_css_vars.py https://example.com
    python extract_css_vars.py https://example.com --output ./tokens.json
    python extract_css_vars.py https://example.com --budget 3000
    python extract_css_vars.py --grep 'border|radius'   # search the saved JSON
    python extract_css_vars.py https://example.com --json   # full JSON to stdout
"""

import argparse
import json
import re
import sys
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import urljoin, urlparse

# Ensure Unicode (✅, etc.) prints cleanly on Windows consoles whose default
# code page is cp1252.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# CSS variable definition. Tolerates whitespace, multiline values, !important.
# Captures: name, value.
CSS_VAR_RE = re.compile(
    r"(?:(?<=[{;\s])|^)--([A-Za-z0-9_-]+)\s*:\s*([^;}]+?)\s*(?:!important\s*)?(?:;|(?=\}))",
    re.DOTALL,
)

# Stylesheet link extraction (rough but reliable for most pages).
LINK_HREF_RE = re.compile(
    r'<link\s+[^>]*rel=["\']?stylesheet["\']?[^>]*>',
    re.IGNORECASE,
)
HREF_ATTR_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)

# Inline <style> blocks.
STYLE_BLOCK_RE = re.compile(
    r"<style\b[^>]*>(.*?)</style>",
    re.IGNORECASE | re.DOTALL,
)

# Heuristic category mapping based on variable name substrings.
CATEGORY_HINTS = [
    ("color",      ("color", "bg", "background", "border", "fg", "foreground", "surface",
                    "text", "accent", "primary", "secondary", "muted", "success",
                    "warning", "error", "danger", "info", "destructive", "ring", "shadow-color")),
    ("spacing",    ("space", "spacing", "gap", "padding", "margin", "inset", "size")),
    ("typography", ("font", "text", "leading", "tracking", "line-height", "letter-spacing",
                    "weight")),
    ("radius",     ("radius", "rounded")),
    ("shadow",     ("shadow", "elevation")),
    ("z-index",    ("z-", "zindex", "z-index", "layer")),
    ("duration",   ("duration", "transition", "delay", "ease")),
    ("breakpoint", ("breakpoint", "screen", "viewport")),
]


def http_get(url, timeout=15):
    """GET a URL, return text content. Returns None on error."""
    req = urlrequest.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except (urlerror.URLError, urlerror.HTTPError, TimeoutError, OSError) as e:
        print(f"   warn: failed to fetch {url}: {e}", file=sys.stderr)
        return None


def find_stylesheet_urls(html, base_url):
    """Extract all stylesheet URLs from the HTML, resolved against base_url."""
    urls = []
    for link_tag in LINK_HREF_RE.findall(html):
        m = HREF_ATTR_RE.search(link_tag)
        if not m:
            continue
        href = m.group(1).strip()
        if href.startswith(("data:", "javascript:", "#")):
            continue
        absolute = urljoin(base_url, href)
        urls.append(absolute)
    return urls


def find_inline_styles(html):
    """Extract content of every inline <style> block."""
    return STYLE_BLOCK_RE.findall(html)


def extract_vars_from_css(css_text):
    """Return list of (name, value) tuples for every --var: value found."""
    pairs = []
    for name, raw_value in CSS_VAR_RE.findall(css_text):
        value = " ".join(raw_value.split())  # collapse whitespace/newlines
        pairs.append((name, value))
    return pairs


def categorize(name):
    """Heuristic: map a variable name to a category bucket."""
    lower = name.lower()
    for category, hints in CATEGORY_HINTS:
        for hint in hints:
            if hint in lower:
                return category
    return "other"


def merge_uniq(pairs):
    """
    Collapse duplicates while preserving first-seen order. If a variable is
    redefined with different values across stylesheets, keep the first and
    record the alternatives in `_overrides`.
    """
    seen = {}
    overrides = {}
    for name, value in pairs:
        if name not in seen:
            seen[name] = value
        elif seen[name] != value:
            overrides.setdefault(name, []).append(value)
    return seen, overrides


def build_output(seen, overrides, url, sources):
    """Build the final grouped JSON document."""
    grouped = {}
    for name, value in seen.items():
        category = categorize(name)
        grouped.setdefault(category, {})[name] = {
            "value": value,
            "source": "css-custom-property",
        }
        if name in overrides:
            grouped[category][name]["alternatives"] = overrides[name]

    return {
        "tokens": grouped,
        "_meta": {
            "source_url": url,
            "stylesheet_count": len(sources),
            "stylesheets": sources,
            "total_variables": sum(len(v) for v in grouped.values()),
            "note": (
                "These are explicit CSS custom properties extracted from the site's "
                "stylesheets. Treat them as ✅ high-confidence tokens — the authors "
                "named them deliberately. Categories are heuristic; review before using."
            ),
        },
    }


NOISE_PREFIXES = ("tw-", "shiki", "radix-", "chakra-", "mantine-", "swiper-", "toastify-",
                  "rdp-", "sx-", "framer-", "animate-", "webkit-", "moz-", "docsearch-",
                  "cf-", "sb-", "intercom-")
SEMANTIC_HINTS = ("primary", "secondary", "accent", "brand", "background", "bg", "surface",
                  "foreground", "fg", "text", "border", "muted", "success", "warning",
                  "error", "danger", "font", "radius", "shadow", "focus", "ring", "link")
DIGEST_SHARES = (
    ("color", 0.36), ("typography", 0.18), ("radius", 0.06), ("shadow", 0.10),
    ("spacing", 0.12), ("breakpoint", 0.04), ("duration", 0.04), ("z-index", 0.02),
    ("other", 0.08),
)
SCALE_RE = re.compile(r"^(.*?)[-_]?(\d+(?:\.\d+)?|[2-9]?x[sl]|sm|md|lg|xl)$")
VAR_REF_RE = re.compile(r"^var\(\s*--([A-Za-z0-9_-]+)\s*(?:,\s*(.+))?\)$")
COLOR_VALUE_RE = re.compile(
    r"^(#[0-9a-f]{3,8}|(rgba?|hsla?|oklch|oklab|lab|lch|hwb|color-mix|color)\(|"
    r"(white|black|transparent|currentcolor)$)",
    re.IGNORECASE,
)
DIMENSION_RE = re.compile(r"^(0|-?[\d.]+(px|rem|em|%|vw|vh|vi|ch)|(clamp|calc|min|max)\(.*)$")
TIME_RE = re.compile(r"^[\d.]+m?s$|cubic-bezier\(|^(ease|linear)(\s|$|-in|-out)")
CHANNELS_RE = re.compile(r"^[\d.]+%?(\s*,\s*[\d.]+%?){2,3}$")
TYPE_HINTS = ("font", "leading", "tracking", "line-height", "letter", "weight", "text-", "heading",
              "title", "display", "body")


def categorize_resolved(name, value):
    lower = name.lower()
    if "radius" in lower or "rounded" in lower:
        return "radius"
    if ("shadow" in lower or "elevation" in lower) and not COLOR_VALUE_RE.match(value):
        return "shadow"
    if "breakpoint" in lower or "screen-" in lower:
        return "breakpoint"
    if lower.startswith("z-") or "-z-" in lower or "z-index" in lower or "zindex" in lower:
        return "z-index"
    if COLOR_VALUE_RE.match(value):
        return "color"
    if TIME_RE.search(value) or "duration" in lower or "ease" in lower:
        return "duration"
    if any(h in lower for h in ("padding", "margin", "gap", "space", "inset")) and DIMENSION_RE.match(value):
        return "spacing"
    if any(h in lower for h in TYPE_HINTS) or "," in value and '"' in value:
        return "typography"
    if DIMENSION_RE.match(value):
        return "spacing"
    return categorize(name)


def resolve_alias(value, table, depth=0):
    m = VAR_REF_RE.match(value.strip())
    if not m or depth > 6:
        return value
    target = table.get(m.group(1))
    if target is None:
        return m.group(2) or value
    return resolve_alias(target, table, depth + 1)


def is_noise(name, value):
    if name.lower().startswith(NOISE_PREFIXES):
        return True
    if CHANNELS_RE.match(value):
        return True
    return len(value) > 90 or "{" in value or value in ("initial", "inherit", "unset", "")


def section_lines(items, overrides, seen):
    scales, singles = {}, []
    for name, value in items.items():
        m = SCALE_RE.match(name)
        if m and m.group(1):
            scales.setdefault(m.group(1), []).append((m.group(2), name, value))
        else:
            singles.append((name, value))
    for stem, members in list(scales.items()):
        if len(members) < 3:
            singles.extend((n, v) for _, n, v in members)
            del scales[stem]

    lines = []
    ranked = sorted(scales.items(), key=lambda kv: (
        not any(h in kv[0].lower() for h in SEMANTIC_HINTS + ("gray", "grey", "neutral")),
        -len(kv[1]),
    ))
    for stem, members in ranked:
        steps = " ".join(f"{step}={value}" for step, _, value in members)
        themed = any(n in overrides for _, n, _ in members)
        lines.append(f"- --{stem}-*: {steps}" + ("  (redefined elsewhere, likely a theme)" if themed else ""))
    singles.sort(key=lambda nv: (not any(h in nv[0].lower() for h in SEMANTIC_HINTS), len(nv[0])))
    for name, value in singles:
        alt = overrides.get(name)
        alt_note = f"  | alt: {resolve_alias(alt[0], seen)}" if alt else ""
        lines.append(f"- --{name}: {value}{alt_note}")
    return [line if len(line) <= 200 else line[:197] + "..." for line in lines]


def build_digest(seen, overrides, url, sources, full_path, budget):
    kept = {n: v for n, v in seen.items() if not is_noise(n, v)}
    by_category = {}
    for name, value in kept.items():
        resolved = resolve_alias(value, seen)
        by_category.setdefault(categorize_resolved(name, resolved), {})[name] = resolved

    out = [
        f"# CSS custom properties: {url}",
        f"{len(seen)} variables in {len(sources)} source(s), {len(seen) - len(kept)} framework "
        f"or noise vars hidden, var() aliases resolved. Full JSON saved to {full_path}; "
        f"to look up more, run this script with --grep 'border|radius' (no refetch) "
        f"instead of reading or parsing the file.",
    ]
    carry, dropped = 0, 0
    for category, share in DIGEST_SHARES:
        items = by_category.get(category)
        allowance = int(budget * share) + carry
        if not items:
            carry = allowance
            continue
        lines = section_lines(items, overrides, seen)
        out.append(f"\n## {category} ({len(items)})")
        used = 0
        for i, line in enumerate(lines):
            if used + len(line) + 1 > allowance:
                dropped += len(lines) - i
                out.append(f"- (+{len(lines) - i} more)")
                break
            out.append(line)
            used += len(line) + 1
        carry = max(0, allowance - used)
    if dropped:
        out.append(f"\n{dropped} lines left out to stay under {budget} chars. "
                   f"Raise --budget or use --grep.")
    return "\n".join(out)


def grep_saved(json_path, pattern, budget):
    from pathlib import Path
    path = Path(json_path)
    if not path.exists():
        return f"{path} not found. Run with a URL first."
    data = json.loads(path.read_text(encoding="utf-8"))
    seen, overrides = {}, {}
    for items in data.get("tokens", {}).values():
        for name, info in items.items():
            seen[name] = info["value"]
            if info.get("alternatives"):
                overrides[name] = info["alternatives"]
    regex = re.compile(pattern, re.IGNORECASE)
    lines, used = [], 0
    matches = [n for n in seen if regex.search(n)]
    for i, name in enumerate(matches):
        alt = overrides.get(name)
        line = f"--{name}: {resolve_alias(seen[name], seen)}"
        if alt:
            line += f"  | alt: {resolve_alias(alt[0], seen)}"
        line = line if len(line) <= 200 else line[:197] + "..."
        if used + len(line) > budget:
            lines.append(f"(+{len(matches) - i} more matches; narrow the pattern)")
            break
        lines.append(line)
        used += len(line) + 1
    return "\n".join(lines) if lines else f"No variable name matches /{pattern}/ in {path}."


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract CSS custom properties (--vars) from a URL. "
            "Stdlib only — no dependencies."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("url", nargs="?", help="URL of the site to inspect")
    parser.add_argument(
        "--grep",
        metavar="REGEX",
        default=None,
        help="Search the JSON saved by a previous run (--output path) by variable name "
             "and print matches with aliases resolved. No network, no URL needed.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./css-vars.json",
        help="Full JSON path (default: ./css-vars.json).",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=6000,
        help="Max characters of the printed digest (default: 6000, about 1.5-2k tokens).",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Print the full JSON to stdout instead of the digest (large: 15-55k tokens "
             "on real marketing sites).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON file (indent=2). Default is compact.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="HTTP timeout per request in seconds (default: 15).",
    )

    args = parser.parse_args()

    if args.grep:
        print(grep_saved(args.output, args.grep, args.budget))
        return
    if not args.url:
        parser.error("a URL is required unless --grep is given")

    parsed = urlparse(args.url)
    if not parsed.scheme:
        print("URL must include scheme (http:// or https://)", file=sys.stderr)
        sys.exit(2)

    print(f"Fetching HTML: {args.url}", file=sys.stderr)
    html = http_get(args.url, timeout=args.timeout)
    if html is None:
        print("Could not fetch the page. Aborting.", file=sys.stderr)
        sys.exit(1)

    all_pairs = []
    sources = []

    inline_blocks = find_inline_styles(html)
    if inline_blocks:
        print(f"Found {len(inline_blocks)} inline <style> block(s).", file=sys.stderr)
        for i, css in enumerate(inline_blocks):
            pairs = extract_vars_from_css(css)
            if pairs:
                sources.append(f"inline-style-{i}")
                all_pairs.extend(pairs)

    stylesheet_urls = find_stylesheet_urls(html, args.url)
    print(f"Found {len(stylesheet_urls)} linked stylesheet(s).", file=sys.stderr)
    for ss_url in stylesheet_urls:
        css_text = http_get(ss_url, timeout=args.timeout)
        if css_text is None:
            continue
        pairs = extract_vars_from_css(css_text)
        if pairs:
            sources.append(ss_url)
            all_pairs.extend(pairs)
            print(f"   {ss_url} → {len(pairs)} vars", file=sys.stderr)

    seen, overrides = merge_uniq(all_pairs)
    output = build_output(seen, overrides, args.url, sources)

    indent = 2 if args.pretty else None
    serialized = json.dumps(output, indent=indent, ensure_ascii=False)

    if args.as_json:
        print(serialized)
        return

    from pathlib import Path
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(serialized, encoding="utf-8")
    print(build_digest(seen, overrides, args.url, sources, out_path, args.budget))


if __name__ == "__main__":
    main()
