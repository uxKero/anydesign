#!/usr/bin/env python3
"""
capture_site.py — Website capture with Playwright (on-demand)

This script runs when raw HTML analysis is insufficient (JS-heavy sites,
SPAs without SSR) or when responsive analysis needs multiple viewports.
Renders the site in a headless Chromium, attempts to dismiss common
cookie/consent banners, then saves a few viewport-sized frames spread from top
to bottom (readable, unlike a 15000px full-page PNG) and prints the computed
styles of typical elements (body, headings, buttons, inputs, cards). Those
styles are real values from the DOM, so they replace reading the HTML.

Basic usage:
    python capture_site.py https://example.com

Multi-viewport capture (for responsive analysis):
    python capture_site.py https://example.com \\
        --viewports desktop,tablet,mobile \\
        --output ./captures/example.png

Scroll capture (for lazy-loaded content):
    python capture_site.py https://example.com --scroll-capture

Element capture (for element mode — screenshots one element only):
    python capture_site.py https://example.com \\
        --selector "header.navbar" \\
        --output ./element.png

    With --selector, the screenshot covers only the element's bounding box and
    the saved HTML is the element's outerHTML instead of the full page.

More or fewer frames, or the old single full-page PNG:
    python capture_site.py https://example.com --frames 2
    python capture_site.py https://example.com --full-page

Also keep the post-JS rendered HTML (large; grep it, never read it whole):
    python capture_site.py https://example.com --save-html

Requirements:
    pip install playwright
    playwright install chromium

If Playwright is not installed, the script prints the exact install command.
"""

import argparse
import sys
from pathlib import Path

# Ensure Unicode (em-dash, etc.) prints cleanly on Windows consoles whose
# default code page is cp1252.
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


VIEWPORT_PRESETS = {
    "desktop": (1440, 900),
    "tablet": (768, 1024),
    "mobile": (375, 812),
}

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Common cookie/consent banner accept-button selectors. Order matters:
# more specific / common patterns first. Each selector is tried with a
# short timeout; failures are silent.
COOKIE_ACCEPT_SELECTORS = [
    'button[id*="accept" i]',
    'button[id*="agree" i]',
    'button[id*="consent" i]',
    'button[class*="accept" i]',
    'button[class*="consent" i]',
    'button[aria-label*="accept" i]',
    'button[aria-label*="agree" i]',
    '[data-testid*="accept" i]',
    '[data-cy*="accept" i]',
    '#onetrust-accept-btn-handler',
    '.cc-accept',
    '.cc-allow',
    '.cookie-accept',
    '.gdpr-accept',
]


def check_playwright_installed():
    """Check if Playwright is available. If not, show clear instructions."""
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        print(
            "Playwright is not installed in this environment.\n\n"
            "To install, run:\n\n"
            "    pip install playwright\n"
            "    playwright install chromium\n\n"
            "Note: the first time, Chromium weighs ~300MB. That's normal.\n"
            "Once installed, run this script again.",
            file=sys.stderr,
        )
        return False


def parse_viewport(viewport_str):
    """Convert '1440x900' into (1440, 900)."""
    try:
        w, h = viewport_str.lower().split("x")
        return int(w), int(h)
    except Exception:
        raise argparse.ArgumentTypeError(
            f"Invalid viewport: {viewport_str}. Expected format '1440x900'."
        )


def parse_viewports_list(viewports_str):
    """
    Convert 'desktop,mobile' or 'desktop,1024x768' into a list of
    (label, (width, height)) tuples. Mixes presets and custom sizes freely.
    """
    out = []
    for item in viewports_str.split(","):
        item = item.strip()
        if not item:
            continue
        if item in VIEWPORT_PRESETS:
            out.append((item, VIEWPORT_PRESETS[item]))
        else:
            try:
                w, h = item.lower().split("x")
                out.append((f"{w}x{h}", (int(w), int(h))))
            except Exception:
                raise argparse.ArgumentTypeError(
                    f"Invalid viewport spec: {item}. Use a preset "
                    f"({', '.join(VIEWPORT_PRESETS)}) or WxH (e.g. 1440x900)."
                )
    if not out:
        raise argparse.ArgumentTypeError("No viewports specified.")
    return out


def dismiss_cookie_banner(page, verbose=True):
    """
    Attempt to click a cookie/consent accept button. Silently fail if none
    match. Returns True if a click landed, False otherwise.
    """
    for selector in COOKIE_ACCEPT_SELECTORS:
        try:
            locator = page.locator(selector).first
            if locator.count() > 0 and locator.is_visible(timeout=500):
                locator.click(timeout=1000)
                if verbose:
                    print(f"   Dismissed banner via selector: {selector}")
                page.wait_for_timeout(500)
                return True
        except Exception:
            continue
    return False


def scroll_through_page(page, steps=(0.25, 0.5, 0.75, 1.0), pause_ms=400):
    """Scroll progressively to trigger lazy-loaded / intersection-observed content."""
    try:
        full_height = page.evaluate("document.body.scrollHeight")
    except Exception:
        return
    for step in steps:
        target = int(full_height * step)
        try:
            page.evaluate(f"window.scrollTo({{ top: {target}, behavior: 'instant' }})")
        except Exception:
            page.evaluate(f"window.scrollTo(0, {target})")
        page.wait_for_timeout(pause_ms)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(pause_ms)


def capture_frames(page, base_path, viewport, frames):
    try:
        height = page.evaluate("document.documentElement.scrollHeight")
    except Exception:
        height = viewport[1]
    max_scroll = max(0, height - viewport[1])
    count = max(1, min(frames, 1 + max_scroll // max(1, viewport[1] // 2)))
    positions = [0] if count == 1 else [round(max_scroll * i / (count - 1)) for i in range(count)]

    paths = []
    stem, suffix = base_path.stem, base_path.suffix or ".png"
    for i, top in enumerate(positions, 1):
        page.evaluate(f"window.scrollTo(0, {top})")
        page.wait_for_timeout(500)
        path = base_path.with_name(f"{stem}-{i:02d}{suffix}")
        page.screenshot(path=str(path))
        paths.append(path)
    page.evaluate("window.scrollTo(0, 0)")
    print(f"   Page height: {height}px, {len(paths)} frame(s) of {viewport[0]}x{viewport[1]}")
    return paths


STYLE_PROBE_JS = r"""
() => {
  const pick = ['font-family','font-size','font-weight','line-height','letter-spacing','color',
                'background-color','border-radius','padding','border','box-shadow','text-transform'];
  const skip = {'letter-spacing':'normal','box-shadow':'none','text-transform':'none',
                'background-color':'rgba(0, 0, 0, 0)','border-radius':'0px','padding':'0px'};
  const visible = el => { const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'; };
  const describe = el => { const cs = getComputedStyle(el); const out = [];
    for (const p of pick) { let v = cs.getPropertyValue(p);
      if (!v || skip[p] === v || (p === 'border' && /^0px/.test(v))) continue;
      if (p === 'font-family') v = v.split(',').slice(0, 2).join(',');
      if (p === 'box-shadow') { v = v.split(/,(?![^(]*\))/).map(x => x.trim())
          .filter(x => !/^rgba\(0, 0, 0, 0\)/.test(x)).join(', '); if (!v) continue; }
      if (p === 'border-radius' && parseFloat(v) > 999) v = '9999px (pill)';
      out.push(`${p}: ${v}`); }
    return out.join('; '); };
  const lines = [];
  const once = (label, selector, limit = 1) => {
    const seen = new Set(); let n = 0;
    for (const el of document.querySelectorAll(selector)) {
      if (n >= limit || !visible(el) || /^skip to/i.test((el.innerText || '').trim())) continue;
      const d = describe(el); if (seen.has(d)) continue;
      seen.add(d); n++;
      const text = (el.innerText || el.value || '').trim().replace(/\s+/g, ' ').slice(0, 28);
      lines.push(`${label}${text ? ` "${text}"` : ''}: ${d}`);
    }
  };
  once('body', 'body');
  ['h1','h2','h3'].forEach(h => once(h, h));
  once('p', 'main p, p', 2);
  once('a', 'main a, a', 2);
  once('button', 'button, a[class*="button" i], a[class*="btn" i], [role="button"]', 4);
  once('input', 'input:not([type="hidden"]), textarea, select');
  once('header', 'header, nav');
  once('card', '[class*="card" i]', 2);
  return lines;
}
"""


def computed_style_digest(page):
    try:
        page.evaluate("window.scrollTo(0, 0)")
        return page.evaluate(STYLE_PROBE_JS)
    except Exception as e:
        return [f"(style probe failed: {e})"]


def output_path_for_viewport(base_path: Path, label: str, total: int) -> Path:
    """
    Build the per-viewport output path. For a single viewport, return base_path
    unchanged. For multiple, insert '-<label>' before the extension.
    """
    if total == 1:
        return base_path
    stem = base_path.stem
    suffix = base_path.suffix or ".png"
    return base_path.with_name(f"{stem}-{label}{suffix}")


def capture_one(
    url,
    output_path,
    viewport,
    label,
    save_html=True,
    dismiss_cookies=True,
    scroll_capture=False,
    selector=None,
    user_agent=DEFAULT_USER_AGENT,
    wait_until="networkidle",
    timeout=30000,
    full_page=False,
    frames=4,
    styles=True,
):
    """Capture a single viewport. Returns the output path."""
    from playwright.sync_api import sync_playwright

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Capturing [{label}] {url}")
    print(f"   Viewport: {viewport[0]}x{viewport[1]}")
    print(f"   Wait until: {wait_until}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": viewport[0], "height": viewport[1]},
            user_agent=user_agent,
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until=wait_until, timeout=timeout)
        except Exception as e:
            print(f"   Page took longer than expected or partial load: {e}")
            print("   Continuing with what rendered so far.")

        # Small extra wait for entry animations
        page.wait_for_timeout(1000)

        if dismiss_cookies:
            dismiss_cookie_banner(page)

        if scroll_capture:
            print("   Scrolling to trigger lazy content...")
            scroll_through_page(page)

        if selector:
            locator = page.locator(selector).first
            try:
                locator.wait_for(state="visible", timeout=10000)
            except Exception:
                browser.close()
                raise RuntimeError(
                    f"Selector matched nothing visible: {selector!r}. "
                    "Try a broader selector, or capture without --selector and "
                    "analyze the element region visually."
                )
            locator.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            box = locator.bounding_box()
            if box:
                print(
                    f"   Element box: {int(box['width'])}x{int(box['height'])} "
                    f"at ({int(box['x'])}, {int(box['y'])})"
                )
            locator.screenshot(path=str(output_path))
            print(f"   Element screenshot saved: {output_path}")

            if save_html:
                html_path = output_path.with_suffix(".html")
                outer_html = locator.evaluate("el => el.outerHTML")
                html_path.write_text(outer_html, encoding="utf-8")
                print(f"   Element outerHTML saved: {html_path}")
        elif full_page:
            page.screenshot(path=str(output_path), full_page=True)
            print(f"   Screenshot saved: {output_path}")
        else:
            for frame_path in capture_frames(page, output_path, viewport, frames):
                print(f"   Frame saved: {frame_path}")

        if styles and not selector:
            print("   Computed styles (from the live DOM, high confidence):")
            for line in computed_style_digest(page):
                print(f"     {line}")

        if not selector:
            if save_html:
                html_path = output_path.with_suffix(".html")
                html_content = page.content()
                html_path.write_text(html_content, encoding="utf-8")
                print(
                    f"   Rendered HTML saved: {html_path} ({len(html_content) // 1024} KB; "
                    "grep it, never read it whole)"
                )

        try:
            title = page.title()
            print(f"   Page title: {title}")
        except Exception:
            pass

        browser.close()

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Capture a website with Playwright. Used when raw HTML is insufficient "
            "or when responsive analysis needs multiple viewports."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("url", help="URL of the site to capture")
    parser.add_argument(
        "--output",
        "-o",
        default="./capture.png",
        help="Output path of the PNG (default: ./capture.png). With --viewports, "
             "the viewport label is appended before the extension.",
    )
    parser.add_argument(
        "--viewports",
        type=parse_viewports_list,
        default=None,
        help=f"Comma-separated viewports (presets: {', '.join(VIEWPORT_PRESETS)}, "
             "or WxH like 1024x768). Default: just desktop.",
    )
    parser.add_argument(
        "--viewport",
        type=parse_viewport,
        default=None,
        help="Legacy single-viewport flag (WxH). Use --viewports for multi-viewport.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=4,
        help="Viewport-sized frames per viewport, spread top to bottom (default: 4).",
    )
    parser.add_argument(
        "--full-page",
        action="store_true",
        help="One full-page PNG instead of frames. Tall pages become unreadable once "
             "a vision model downscales them; prefer frames.",
    )
    parser.add_argument(
        "--no-styles",
        dest="styles",
        action="store_false",
        default=True,
        help="Skip the computed-style digest.",
    )
    parser.add_argument(
        "--save-html",
        dest="save_html",
        action="store_true",
        default=None,
        help="Save the rendered HTML (default: off for pages, on for --selector, "
             "where it is the element's outerHTML).",
    )
    parser.add_argument(
        "--no-save-html",
        dest="save_html",
        action="store_false",
        help="Never save HTML, not even the element's outerHTML.",
    )
    parser.add_argument(
        "--no-dismiss-cookies",
        dest="dismiss_cookies",
        action="store_false",
        default=True,
        help="Disable the cookie/consent banner auto-dismiss attempt.",
    )
    parser.add_argument(
        "--selector",
        default=None,
        help="CSS selector for element capture: screenshot only the first matching "
             "element's bounding box and save its outerHTML instead of the full page. "
             "Used by element mode ('copy element').",
    )
    parser.add_argument(
        "--scroll-capture",
        action="store_true",
        help="Scroll through the page (25%%/50%%/75%%/100%%) before screenshot to "
             "trigger lazy-loaded content.",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="Custom user-agent string (default: Mac Chrome 120).",
    )
    parser.add_argument(
        "--wait-until",
        choices=["load", "domcontentloaded", "networkidle"],
        default="networkidle",
        help="When to consider the page loaded (default: networkidle)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30000,
        help="Timeout in milliseconds (default: 30000)",
    )

    args = parser.parse_args()

    if not check_playwright_installed():
        sys.exit(2)

    if args.viewports:
        viewports = args.viewports
    elif args.viewport:
        viewports = [(f"{args.viewport[0]}x{args.viewport[1]}", args.viewport)]
    else:
        viewports = [("desktop", VIEWPORT_PRESETS["desktop"])]

    base_path = Path(args.output)
    total = len(viewports)

    try:
        for label, viewport in viewports:
            out = output_path_for_viewport(base_path, label, total)
            capture_one(
                url=args.url,
                output_path=out,
                viewport=viewport,
                label=label,
                save_html=args.save_html if args.save_html is not None else bool(args.selector),
                dismiss_cookies=args.dismiss_cookies,
                scroll_capture=args.scroll_capture,
                selector=args.selector,
                user_agent=args.user_agent,
                wait_until=args.wait_until,
                timeout=args.timeout,
                full_page=args.full_page,
                frames=args.frames,
                styles=args.styles,
            )
    except Exception as e:
        print(f"Error during capture: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
