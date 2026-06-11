# Changelog

All notable changes to `anydesign` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- **`examples/game-asset-pack/`** — the game-dev use case for element mode:
  one extraction → N consistent assets. A toon battle-royale key art becomes a
  **prompt pack** (shared style base + three isolated asset prompts: original
  character, pickup, prop), with color-allocation rules captured as consistency
  notes ("energy green is VFX-only"). Downstream proof: `asset-character.png`
  generated with real alpha and the palette grounding held. New "Act 4" in the
  README showcase.

---

## [0.5.1] — 2026-06-11

### Added — asset delivery format + asset-path validation

- **Delivery format for `asset`/`hybrid` prompts** in `references/element-copy.md`:
  `scene` (background baked in, edges blending into the destination surface) vs
  `isolated` (single subject on a **transparent background / PNG with alpha**,
  generous margin — for dropping the asset into a web). Defaults to `isolated` when
  the user's goal is placement ("for my website", "as a PNG"). Per-model
  transparency notes: gpt-image native (`background: "transparent"`), Midjourney
  flat-bg + removal, SD/Flux flat-bg + removal.
- **Defensive isolated-prompt rules**, learned from a real failure: prose requests
  for transparency are unreliable in chat UIs, and style worlds summon backdrops
  and extra characters. Isolated prompts now lead with the isolation directive,
  strip world/atmosphere words, keep lighting neutral, and close with "no
  background of any kind" — with a chroma-key fallback documented for models
  without true alpha.
- **`examples/discord-hero-asset/`** — validation of the asset path with proof for
  **both delivery formats**: discord.com's clay-style 3D hero scene →
  token-grounded image prompt → `element-3D.png` (scene, **first pass**: indigo
  ramp held, accents on the extracted hexes, scarce pink scoped to the screen UI,
  original characters per the IP guardrail) and `element-3D-isolated.png`
  (isolated cutout with verified real alpha — 65% transparent / 22% opaque / 13%
  antialiased edges).

---

## [0.5.0] — 2026-06-10

### Added — Element mode ("copy element")

- **New mode that scopes the analysis to ONE visual element** — "copy this navbar",
  "recreate this 3D illustration", "give me a prompt to regenerate this graphic".
  Instead of a system-level `design.md`, element mode produces a focused **`element.md`**.
- **Three element kinds with distinct outputs**:
  - `code` (navbar, card, button, hero) → scoped token spec + ready-to-paste
    reconstruction prompt for code agents (v0, Claude Code, Lovable)
  - `asset` (3D illustrations, mascots, photographic art) → **token-grounded prompt
    for generative image models**: the prompt embeds the exact extracted palette
    (hex via `extract_colors.py` / CSS vars / Figma fills), observed lighting,
    composition, and the parent brand's mood — plus negative cues and per-model
    adaptation notes (gpt-image/DALL-E, Midjourney, Stable Diffusion/Flux)
  - `hybrid` (a code container embedding art) → code spec + nested asset prompt(s)
- **`references/element-copy.md`** — the new reference: classification heuristic,
  element-scoped capture flows, the full `element.md` template (YAML frontmatter +
  prose, `anydesign-element-1` schema), structured canonical prompt format
  (SUBJECT / STYLE / COMPOSITION / LIGHTING / PALETTE / MOOD / INTEGRATION / AVOID),
  and element-mode quality rules — including an IP guardrail for brand-identifying
  artwork and a mandatory prompt-fidelity honesty note.
- **`--selector` flag in `scripts/capture_site.py`** — DOM-precise element capture:
  screenshots only the first matching element's bounding box and saves its
  `outerHTML` instead of the full page. Composes with `--viewports`. Clear error
  (exit 1) when the selector matches nothing visible. Tested live against
  vercel.com's header (1440×64 crop + outerHTML).
- SKILL.md: new "Two modes" routing section (full vs element, with activation
  signals and ambiguity rule), element-mode trigger phrases in the skill
  description, updated scripts table and structure tree.
- README: new "Copy a single element (element mode)" section, element use case,
  and updated script docs.
- **`examples/poolsuite-player-element/`** — first real-world element-mode run:
  the retro Mac OS player window of poolsuite.net, captured via
  `--selector "#component-is-fm"` (607×640 + outerHTML). The `element.md` is a
  `hybrid`: scoped spec (pixel-sampled accents, verbatim bevel shadows, the
  `active:invert` signature interaction), v0-ready reconstruction prompt, and a
  token-grounded VHS-still image prompt. Downstream proof: the prompt pasted into
  v0 produced a live rebuild at
  [retro-radio-player-zz.vercel.app](https://retro-radio-player-zz.vercel.app/)
  in two iterations — the second fixing typographic case discipline, a lesson
  fed back into `element-copy.md` as a first-class capture rule.

### Notes

- `lint_design_md.py` validates the full `design.md` contract only — it does not
  apply to `element.md`.
- Element mode delivers the **prompt**, never the rendered image — generation stays
  in the user's image model of choice.

---

## [0.4.0] — 2026-05-19

### Added — Claude Design bridge

- **`scripts/export_for_claude_design.py`** — packages a `design.md` (+ optional
  `design-tokens.json`) into a multi-format bundle ready to upload as "brand and product
  assets" in [claude.ai/design](https://claude.ai/design). Emits:
  - `brand-kit.pptx` — cover, atmosphere, color swatches (paginated), typography samples,
    spacing/radii, components, Do's/Don'ts, reconstruction notes
  - `brand-overview.docx` — the full `design.md` rendered as Word (headings, paragraphs,
    bullets, tables preserved)
  - `tokens.css` — `:root { --... }` CSS custom properties from DTCG tokens
  - `tailwind.config.ts` — Tailwind v3 config (colors, fontFamily, fontSize, fontWeight,
    spacing, borderRadius, boxShadow) from DTCG tokens
  - `README-claude-design.md` — step-by-step upload instructions
- Bridge is necessary because Claude Design does not (yet) ingest DTCG JSON or markdown
  directly — it reads PPTX/DOCX/code-repo. This script converts anydesign's outputs into
  the formats Claude Design's design-system extractor accepts, getting your captured
  brand into the org-scoped design system persistently.
- Graceful skip when optional deps (`pyyaml`, `python-pptx`, `python-docx`) aren't
  installed — formats whose deps are missing are emitted as `(skipped: install ...)`.

### Added — README

- New top-level "Use with Claude Design" section in `README.md` covering the workflow
  and artifact-to-Claude-Design-input mapping.

---

## [0.3.0] — 2026-05-18

Major release. Closes the analytical-depth gap with hand-curated competitors
while keeping every differentiator (auto-extraction, confidence markers, DTCG,
WCAG, standalone scripts). Adds three new scripts (lint, verify, plus updates
to existing four). Every generated design.md now ships with YAML frontmatter
+ token refs + 6 analytical layers + Art Direction Patterns QA pass.

### Added — syntax + validation (Sprint 3)

- **YAML frontmatter at the top of every generated design.md** — structured tokens
  (colors, typography, spacing, rounded, components) declared as YAML, parseable
  mechanically by any agent. Required fields: `version`, `name`, `source`,
  `captured_at`, `description`. Schema version: `anydesign-1`.
- **`{token.refs}` syntax** for the prose body — `{colors.primary}`, `{rounded.sm}`,
  `{typography.display}` etc. Convention: reference in the prose followed by the literal
  value in parens for human readability. Makes the design.md refactor-safe.
- **`scripts/lint_design_md.py`** — new stdlib-only validator. Checks: frontmatter
  exists and has required fields, every `{token.ref}` in the body resolves to a
  declared token, every component named in YAML `components:` has a matching prose
  heading (1:1 enforcement), Section 6 Do's/Don'ts non-empty (or carries abstain
  justification), Section 7 Open Questions non-empty. Returns exit 1 on failures so
  it can wire into pre-commit hooks.
- analysis-framework.md now instructs the model to use `{token.refs}` in prose.
- Vercel and Lumen examples updated with frontmatter + refs; both lint clean
  (6 pass · 0 warn · 0 fail).

### Added — differentiator audit (Sprint 4)

- **`scripts/verify_design.py`** — the audit tool. Takes a `design-tokens.json`
  (DTCG) and a live URL, fetches the current CSS custom properties, and reports
  drift by VALUE comparison: which declared tokens still match, which have drifted
  (changed/deprecated), which new CSS values appear that weren't in the original
  extraction scope. This is the differentiator that catalog-based competitors
  cannot replicate — answer to "is the design.md I wrote three months ago still
  accurate?" Output as markdown or JSON. Stdlib only.
- Tested end-to-end against vercel.com: 96 declared tokens still match the live CSS,
  0 drift, 106 new hex values detected in scope-expanded current site.

### Added — analytical depth (Sprint 2)

- **Section 1.2 "Brand voice / Atmosphere"** in every generated `design.md` — 2-3
  dense paragraphs of philosophical prose that explain the *why* behind the surface
  choices, not just the surface description. Forces specific design follow-ons rather
  than generic "modern and clean" copy.
- **Section 1.3 "The 'ONE brand thing'"** — identifies the single element that does
  the brand work alone (the gesture you'd remove last because removing it collapses
  the identity). Documents: what it is, why it carries the brand, how everything else
  is restrained to support it, where it appears and where it deliberately doesn't.
- **Art Direction Patterns QA pass** at the end of `analysis-framework.md` — a
  non-negotiable checklist of patterns shallow analysis routinely misses, grouped
  by category: surface-rhythm patterns (polarity flips, atmospheric gradient scoping,
  density alternation), token coexistence (pill scale, mono usage, weight ceilings,
  tracking discipline), color discipline (voltage allocation, alpha overlays,
  feedback color restraint), elevation discipline (stacked vs single drops,
  inset-shadow-as-border, surface-tone elevation), composition discipline (split vs
  centered hero, asymmetric whitespace, image treatment).
- Methodology guidance in Layer 1 of the framework for Brand voice writing (with
  working examples for Vercel / Linear / Apple) and the ONE-brand-thing heuristic
  (with common shapes: chromatic moment, typographic gesture, geometric move,
  decoration scoping rule).
- Vercel example: new Brand voice paragraph ("Engineering quietude...") and ONE
  brand thing identified (the mesh gradient with scoping discipline).
- Synthetic Lumen example: Brand voice ("a tool for people who think in terminals")
  and ONE brand thing (the scarcity-applied emerald accent).
- SKILL.md updated to surface the QA pass as part of Step 3.

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
