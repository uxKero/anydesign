# Changelog

All notable changes to `anydesign` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added — structural depth (Sprint 1)

- **Section 6: Do's and Don'ts** — new mandatory section in every generated `design.md`.
  Brand-specific usage rules (5-7 of each) grounded in observation, citing tokens
  explicitly. Skill is instructed to abstain rather than pad with generic UX advice
  if evidence is thin.
- **Layer 6 in the analysis framework** — new top-level analytical layer for brand
  rules, with categories (color discipline, typography discipline, elevation
  discipline, etc.) and explicit "when to abstain" guidance.
- **Elevation system tiers** (Section 2.5) — restructured from a flat "Shadows" list
  to a named Level 0-N table with `treatment` + `use` per level, plus a new
  `Decorative depth` subsection for polarity flips, atmospheric gradients, and
  background patterns.
- **Signature components** (Section 3.2) — new subsection separating
  brand-distinctive UI motifs (e.g., Vercel's mesh-gradient hero, polarity-flipped
  bands, dot-grid pattern) from generic primitives. Explicit "no signatures detected"
  fallback when patterns are generic.
- **Responsive behavior table** (Section 4.3) — formal Breakpoints / Touch targets /
  Collapsing strategy structure replacing the previous prose-only mention.
- **Image behavior** (Section 4.4) — new subsection categorizing images by role
  (decorative gradient, brand logo, product mockup, photography, icons) with
  per-category treatment specs.
- Vercel example updated to demonstrate all five new structural pieces; includes
  4 signature components, 7-level elevation table, populated responsive behavior
  (honest about desktop-only confidence), 7 Do's + 7 Don'ts.
- Synthetic landing-example updated for consistency with the new spec.

### Added — earlier
- Real end-to-end example: `examples/vercel-landing/` — full analysis of vercel.com
  produced by running the skill against the live site (`design.md`,
  `design-tokens.json`, `design-a11y.md`, real desktop screenshot). 808 CSS custom
  properties extracted from the live Geist design system. Demonstrates the URL flow
  on a recognizable production site, including a real Geist token map and contrast
  report.
- Downstream-consumption demo: `examples/v0-downstream-demo/` — screenshot of a
  v0-generated app built from a `design.md` produced by this skill, with live URL
  ([v0-anydesignexample.vercel.app](https://v0-anydesignexample.vercel.app/)). Proves
  the output is portable across AI builders.

### Changed
- README rewritten with a hero image (the v0 downstream demo) and explicit portability
  positioning. New sections: "Works with any AI builder" (compatibility table) and
  "Standalone CLI scripts" (the four Python tools are usable without Claude).

---

## [0.2.0] — 2026-05-18

### Added
- New companion script `scripts/extract_css_vars.py` — stdlib-only CSS custom properties
  extractor. Fetches the HTML of a URL, discovers every linked stylesheet and inline
  `<style>` block, and emits a JSON document grouped by heuristic category. These extracted
  variables are treated as ✅ high-confidence tokens in the output.
- New companion script `scripts/extract_colors.py` — Pillow-based dominant color extractor
  for local images. Useful when multimodal vision approximates and you need pixel-precise
  hex codes.
- New companion script `scripts/check_contrast.py` — stdlib-only WCAG 2.1 contrast checker.
  Takes one or more `fg,bg` hex pairs (or a pairs file) and emits a markdown table with
  AA/AAA pass/fail for normal and large text. Produces the optional `design-a11y.md`
  companion file.
- Multi-viewport support in `scripts/capture_site.py` via `--viewports desktop,tablet,mobile`
  (also accepts custom `WxH` specs). Produces per-viewport screenshots with sensible
  defaults (1440×900, 768×1024, 375×812).
- Cookie/consent banner auto-dismiss in `scripts/capture_site.py` via a list of common
  selectors (with silent fallback if nothing matches). Disable with `--no-dismiss-cookies`.
- Scroll-capture mode in `scripts/capture_site.py` (`--scroll-capture`) to trigger
  lazy-loaded / intersection-observed content before the screenshot.
- Configurable user-agent in `scripts/capture_site.py` (`--user-agent`).
- New `Step 2.2.bis` in `references/capture-flows.md` documenting the CSS variables
  extraction flow as part of the URL capture pipeline.
- New `Layer 2.7` in `references/analysis-framework.md` covering accessibility signals
  (WCAG contrast quick-checks).
- New `Section 5.4` in `references/analysis-framework.md` flagging responsive coverage as
  a gotcha and pointing at the multi-viewport capture command.
- `examples/landing-example/` — a full sample analysis of a fictional SaaS landing
  ("Lumen Notes") demonstrating the complete output: `source.md`, `design.md`,
  `design-tokens.json`, `design-a11y.md`.
- `requirements.txt` with optional Python dependencies grouped by script.

### Changed
- `design-tokens.json` now uses the **W3C Design Tokens Community Group (DTCG)** format
  with `$value` / `$type` (canonical, stable since Oct 2025). The legacy
  `{ "value": ..., "confidence": ... }` shape remains supported on request. Confidence
  markers now live under `$extensions.anydesign.confidence`, keeping the output
  spec-compliant for Style Dictionary, Figma Variables, Tokens Studio, and other
  DTCG-aware tooling.
- `scripts/capture_site.py` now **saves the rendered HTML by default** (opt-out with
  `--no-save-html`). The previous default of off forced an opt-in that the skill almost
  always needed.
- Tool name references updated to canonical Claude Code form: `web_fetch` → `WebFetch`
  across SKILL.md and all `references/*.md` files.
- `description` in SKILL.md frontmatter converted from a YAML block scalar (`>`) to a
  plain single-line string, ensuring the skill loader parses it correctly. Trigger
  phrases preserved.
- README.md updated for v0.2.0: documents the new optional scripts, the DTCG format,
  the `examples/` folder, and the accessibility use case.

### Fixed
- Frontmatter no longer relies on YAML block scalar syntax (which some skill loaders
  handle inconsistently).

### Removed
- Mentions of complementary skills that were not part of the public surface
  (`promptdiff`, `multiagent-architect`) have been removed from SKILL.md.

---

## [0.1.0] — 2026-05-18

### Added
- Initial release of the `anydesign` skill.
- Support for three input sources:
  - Local images (PNG, JPG, WebP) via direct multimodal vision
  - Website URLs via hybrid flow (`WebFetch` for HTML, on-demand Playwright for JS-heavy sites)
  - Figma files via Figma MCP (`get_metadata`, `get_variable_defs`, `get_design_context`, `get_screenshot`)
- 5-step structured workflow: identify → capture → analyze → generate → deliver.
- 5-layer analysis framework: identity → system → components → layout → reconstruction.
- Dual output: `design.md` (human-readable) + `design-tokens.json` (machine-readable).
- Confidence markers (✅ high / ⚠️ medium / ❓ low) on every inference.
- Mandatory "Open Questions" section in every output.
- On-demand Playwright capture script (`scripts/capture_site.py`) with full-page screenshot
  and optional rendered-HTML saving.
- Four reference files loaded progressively:
  - `references/capture-flows.md`
  - `references/analysis-framework.md`
  - `references/token-extraction.md`
  - `references/output-template.md`

### Notes
- This is the first public release. The skill has been designed around real workflows
  (replicating references, briefing AI builders, auditing Figma handoffs) but has not yet
  been extensively benchmarked. Feedback welcome.
