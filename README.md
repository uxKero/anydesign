# anydesign

> A Claude skill that analyzes images, websites, and Figma files and generates a `design.md`
> with token system, component inventory, and reconstruction notes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skill Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](./CHANGELOG.md)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-purple.svg)](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)

`anydesign` turns any visual reference — a screenshot, a live website, a Figma file — into a
structured design document that another AI (or a human) can read and use to **reconstruct,
replicate, or document** the design with rigor.

It's not a description generator. It's a **design diagnostics** tool.

---

## What you get

When you point `anydesign` at a visual source, it produces:

1. **`design.md`** — a 7-section structured document:
   - Source metadata and capture method
   - TL;DR (2-3 sentences with the actionable insight)
   - Visual identity (personality, mood, references)
   - Design system (tokens: colors, typography, spacing, radii, shadows, borders)
   - Components inventory (variants, states, sizes)
   - Layout & composition (grid, breakpoints, rhythm)
   - Reconstruction notes (stack, quick wins, tricky bits, confidence map)
   - Open questions (what couldn't be determined)

2. **`design-tokens.json`** *(when concrete tokens were extracted)* — structured tokens in
   the [W3C Design Tokens Community Group (DTCG)](https://www.designtokens.org/) format
   (`$value`/`$type`), ready to feed into Style Dictionary, Figma Variables, Tokens Studio,
   or any DTCG-compliant tooling.

3. **`design-a11y.md`** *(optional)* — WCAG 2.1 contrast report for the extracted color
   pairs (text on surface, primary on surface, etc.), with AA/AAA pass-fail markers.

Every inference is marked with a **confidence level** (✅ high / ⚠️ medium / ❓ low) so the
output is honest about what was directly observed vs. reasonably inferred.

See [`examples/`](./examples) for a full sample analysis on a real site.

---

## Why this exists

Most "describe this design" prompts produce poetic but unactionable output. You get adjectives
("modern", "clean") instead of hex codes. You get vibes instead of a spacing scale. And you
can't hand the result to Claude Code or v0 and expect anything coherent.

`anydesign` is the opposite: it's built so its output is **machine-readable enough** to seed a
build, and **human-readable enough** to brief a designer.

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/uxKero/anydesign.git
```

### 2. Copy the skill folder into your Claude skills directory

```bash
# For personal skills (all projects)
cp -r anydesign ~/.claude/skills/

# OR for a single project
cp -r anydesign /path/to/project/.claude/skills/
```

### 3. (Optional) Install Python dependencies for the companion scripts

The skill works without any Python deps for image and well-formed-HTML sources. Two of the
four companion scripts have optional dependencies:

```bash
pip install -r requirements.txt
playwright install chromium  # only if you'll use capture_site.py
```

The first-time Chromium install is ~300MB.

| Script | Needs |
|---|---|
| `capture_site.py` | `playwright` + Chromium |
| `extract_css_vars.py` | stdlib only |
| `extract_colors.py` | `Pillow` |
| `check_contrast.py` | stdlib only |

### 4. (Optional) Connect the Figma MCP

To analyze Figma files, connect the Figma MCP from the Claude app
(`Settings → Connectors`). The skill uses these tools when available:
`get_metadata`, `get_variable_defs`, `get_design_context`, `get_screenshot`.

---

## Use cases

The skill activates automatically when Claude detects design-analysis intent in your message.
You don't need to write "use anydesign". Here are real scenarios:

### 🎨 Replicating a reference for a client project

> *"I love how Linear's landing page feels. Can you analyze it so I can brief my team on
> something similar for our SaaS?"*

The skill fetches the HTML of linear.app, identifies it as content-rich (no Playwright
needed), extracts CSS custom properties from the linked stylesheets as explicit tokens, and
produces a `design.md` you can paste into a Notion brief. You also get `design-tokens.json`
in DTCG format to feed straight into Style Dictionary or Figma Variables.

### 🧩 Extracting tokens from a Pinterest reference

> *"I have this screenshot saved from Dribbble. Pull the palette and typography so I can
> start building a moodboard."*

You upload the PNG. The skill uses direct vision to extract colors with hex codes (and
optionally calls `extract_colors.py` for pixel-precise dominant colors), identifies the
likely typeface, infers the spacing unit, and marks each inference with a confidence level.
The "Open Questions" section tells you what you'd need a clearer reference for.

### 🛠️ Briefing Claude Code for a from-scratch build

> *"I want a portfolio site that looks like vercel.com but simpler. Generate a design brief
> I can hand to Claude Code."*

The skill analyzes vercel.com, then frames the output with **Reconstruction emphasis** — Section
5 ("Reconstruction Notes") gets the most detail, with stack recommendations, quick wins, and
tricky bits. You take that `design.md`, drop it as context into a new Claude Code session, and
get a starting point that's actually faithful to the reference.

### 🎯 Auditing a Figma file before handoff to dev

> *"Here's the Figma file for our new dashboard. Make sure the tokens are consistent before I
> send it to engineering."*

The skill uses the Figma MCP to pull `get_variable_defs` (explicit tokens defined by the
designer) and `get_design_context` (actual usage). It cross-references both and flags
inconsistencies in the "Open Questions" section — like spacing values that don't match the
declared scale.

### 🔍 Comparing design vs. production implementation

> *"Here's the Figma file and here's the live site. Did the team build what was designed?"*

You pass both. The skill analyzes each and adds an extra **discrepancies** section: tokens
that diverged, components that look different, missing states.

### 📚 Documenting a legacy product's visual language

> *"We've never had a design system. Can you extract one from our current production site?"*

The skill scans your site, infers the implicit system (the one your team built without naming
it), and gives you a starting point for a real design system: documented colors, typography
scale, component variants observed. You now have a baseline to refine instead of starting
from zero.

### ♿ Accessibility quick-check on a brand palette

> *"We have a brand palette. Do the text/background combinations meet WCAG AA?"*

After tokens are extracted, the skill runs `check_contrast.py` over the relevant pairs and
emits `design-a11y.md` with the WCAG 2.1 ratios and pass/fail markers for AA and AAA (both
normal and large text). You see at a glance which combinations need adjusting.

---

## How the skill thinks

It follows a strict 5-step workflow that you can read in detail in [SKILL.md](./SKILL.md):

```
Step 1 — Identify source and emphasis
   ↓
Step 2 — Capture material
         (vision / HTML + CSS vars / Playwright multi-viewport fallback / Figma MCP)
   ↓
Step 3 — Layered analysis (Identity → System → Components → Layout → Reconstruction)
   ↓
Step 4 — Generate design.md + design-tokens.json (+ optional design-a11y.md)
   ↓
Step 5 — Deliver + suggest next step
```

The "layered analysis" goes from general to specific — never jumping from "mood" to "tokens"
without passing through "system". This is what makes the output coherent instead of just a
list of observations.

---

## Project structure

```
anydesign/
├── SKILL.md                       Main instructions (the "brain")
├── README.md                      This file
├── LICENSE                        MIT
├── CHANGELOG.md                   Version history
├── requirements.txt               Optional Python deps for companion scripts
├── references/                    Loaded on-demand during workflow
│   ├── capture-flows.md           How to capture each source type
│   ├── analysis-framework.md      The 5 analysis layers in detail
│   ├── token-extraction.md        How to infer tokens with rigor
│   └── output-template.md         design.md template
├── scripts/                       Optional companion scripts
│   ├── capture_site.py            Multi-viewport Playwright capture
│   ├── extract_css_vars.py        CSS custom properties extractor
│   ├── extract_colors.py          Dominant color extractor (images)
│   └── check_contrast.py          WCAG contrast checker
└── examples/                      Sample outputs of the skill
    ├── README.md
    └── landing-example/
```

The skill uses **progressive disclosure**: `SKILL.md` stays compact, and reference files load
only when the workflow reaches the corresponding step. This keeps Claude's context window
efficient.

---

## Design principles

These are the rules the skill follows internally — they're also useful to know if you want to
extend or fork:

1. **Honesty over confidence.** Every inference carries a confidence marker.
2. **Real values, not literary approximations.** `#3B82F6`, not "sky blue".
3. **Semantic roles, not just enumerations.** `primary`, not "color 1".
4. **Don't invent variants.** If only one button was seen, report one variant.
5. **Don't assume frameworks.** Only claim "this is Tailwind" if classes prove it.
6. **Open Questions section is mandatory.** Or its justified absence.
7. **Extracted > inferred.** A token pulled from a real CSS variable beats a token guessed
   from a pixel — and the confidence marker should reflect that.

---

## Limitations (read before relying on the output)

- **JS-heavy sites without Playwright installed** → skill will tell you and stop. Install
  Playwright or provide a manual screenshot.
- **Cloudflare/captcha-protected sites** → skill won't bypass. It will tell you and ask for a
  manual screenshot.
- **Low-resolution images** → skill will ask for a better version rather than invent details.
- **Partial captures** (only the header visible) → skill will analyze what's there but warn
  about scope.
- **Custom typography** → identification is visual-inference only. The skill will say "looks
  like Inter" rather than assert it definitively.
- **Cookie banners covering content** → `capture_site.py` attempts auto-dismiss via common
  selectors, but cannot guarantee success on every implementation. Manual screenshot remains
  a fallback.

---

## Roadmap

Ideas being considered. None of these are in v0.2.

- **`anydesign-compare`** — sibling skill for explicit A vs B analysis of two sources
- **Quick-scan mode** — express analysis for moodboards (single-paragraph output)
- **Design-vs-implementation diff** — automatic discrepancy detection when both Figma and
  production site are provided
- **Token export adapters** — generate Tailwind config, Style Dictionary build, or Figma
  Variables JSON directly from the DTCG output

If you want to push any of these forward, open an issue or a discussion.

---

## Contributing

Contributions welcome. The skill is small and easy to fork. If you want to propose changes:

1. Fork the repo
2. Make your changes
3. Test the skill locally by copying to `~/.claude/skills/` and asking Claude to analyze a
   couple of real sources
4. Open a pull request describing what you changed and why

For new ideas, open an issue first to discuss the direction before writing the code.

---

## License

MIT. See [LICENSE](./LICENSE).
