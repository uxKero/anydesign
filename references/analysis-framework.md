# Analysis Framework — The 5 analysis layers

This reference defines how to analyze the captured material. Consult it when you start Step 3
of the main workflow.

Analysis goes **from general to specific**, from intent to detail. Don't skip layers: jumping
from "mood" to "tokens" without passing through "system" loses the why.

---

## Layer 1 — Visual identity

**Guiding question:** *What does this design want to be?*

Before measuring, feel. This layer is interpretive but not vague: every statement is justified
with concrete observations.

### What to identify

- **Personality** (3-5 adjectives): professional / playful / minimalist / brutalist / corporate
  / artisanal / technical / warm / clinical / editorial / experimental
- **Stylistic references** (if you recognize them): "Linear-like aesthetic", "Stripe-like",
  "Anthropic homepage", "Notion-ish", "Apple editorial", "new Gumroad-style web brutalism"
- **Mood**: what emotion does it convey? Confidence? Energy? Calm? Urgency?
- **Information density**: minimalist / balanced / dense / saturated
- **Implicit positioning**: who does it speak to? Developers? Enterprise? End consumers?
  Creatives?

### How to justify (no vagueness)

❌ Bad: "Modern and professional design"
✅ Good: "Professional/clinical. Geometric sans typography, restricted palette of
white/black/single blue, lots of whitespace. Reminiscent of Linear or Vercel."

### Common trap

Don't confuse "modern" with analysis. "Modern" means nothing — everything current looks
"modern". Talk about **what makes** it look current: variable typography, generous spacing,
cool neutrals, implicit micro-interactions, etc.

---

## Layer 2 — System (tokens)

**Guiding question:** *Which system-level decisions repeat?*

Here you move from feeling to measurement. Every observed token is documented with its
concrete value.

### Sub-layers

**2.1 Colors**
- List observable colors with hex codes (no approximations)
- Assign inferred semantic role: `primary`, `secondary`, `accent`, `surface`,
  `surface-elevated`, `text-primary`, `text-muted`, `border`, `success`, `warning`, `error`
- Detect **extended palette** if present (e.g., shades of the same color used as a scale)
- If dark mode is visible, document both modes

**2.2 Typography**
- Detected family/families. If you can identify it by name, do so. If not, describe it
  ("geometric condensed sans", "transitional serif", "mono with ligatures")
- Observable scale: which sizes repeat? (h1, h2, body, caption, etc.) in px or rem
- Weights used: 300 / 400 / 500 / 600 / 700
- Approximate line-height per level
- Notable tracking (letter-spacing): if present, note it

**2.3 Spacing**
- Infer the **base unit** (4px, 8px, 16px are most common)
- List observable multiples: 4, 8, 12, 16, 24, 32, 48, 64...
- Mark if it seems consistent (✅) or erratic (⚠️)

**2.4 Radii**
- List observable radii in components: `0` (square), `4px`, `8px`, `12px`, `16px`,
  `pill` (full-rounded)
- Detect if there's a system (e.g., "everything uses 8px except buttons at 6px")

**2.5 Shadows and elevation**
- If shadows exist, note their intensity: none / subtle / medium / strong
- Is there an inferable elevation system? (sm / md / lg)

**2.6 Borders**
- Default thickness, color, style
- Differentiated border states (hover, focus)

**2.7 Accessibility signals** *(optional but recommended when tokens are extracted)*
- Once you have at least two color tokens (e.g., `text-primary` and `surface`, `primary` and
  `surface`), run a contrast check on the key pairs.
- Use `python scripts/check_contrast.py --pair "#111827,#FFFFFF" --pair "#3B82F6,#FFFFFF"`
  to get WCAG 2.1 ratios as a markdown table.
- Thresholds to flag:
  - **AA normal text**: ≥ 4.5:1
  - **AA large text** (18pt+ or 14pt+ bold): ≥ 3:1
  - **AAA normal**: ≥ 7:1
  - **AAA large**: ≥ 4.5:1
- Emit the output as a companion `design-a11y.md` and reference it from Section 7 of the
  `design.md`.

### For extracting tokens with rigor

Consult `token-extraction.md` for detailed methodology on inferring tokens from pixels and
on the DTCG output format.

---

## Layer 3 — Components

**Guiding question:** *Which reusable pieces form this design?*

Inventory the visible components, with their variants and states.

### Typical catalog to look for

- **Buttons**: variants (primary, secondary, ghost, destructive, icon-only), sizes, states
  (default, hover if visible, disabled if visible)
- **Inputs**: text, search, textarea, select, checkbox, radio, toggle. States (empty, filled,
  error, disabled)
- **Cards**: is there a card pattern? What does it contain? Are there variants (simple card,
  card with header, card with cover image)
- **Navigation**: navbar, sidebar, breadcrumbs, tabs, pagination
- **Feedback**: alerts, toasts, badges, tags, banners, modals
- **Typography as component**: headings, eyebrow text, captions, links
- **Lists and tables**: row style, separators, headers
- **Avatars and media**: image treatment, icons (inferable set: Lucide, Heroicons, Phosphor,
  Material Icons)

### Suggested format

For each component:
```
### Button
- Detected variants: primary (solid blue), ghost (transparent with border)
- Sizes: md (40px tall), sm (32px tall)
- Visible states: default, disabled (reduced opacity)
- Notes: generous horizontal padding (~24px), 6px radius
- Confidence: ✅ high (seen in multiple contexts)
```

### Common trap

Don't invent variants. If you only saw one button, say "1 variant observed" — don't assume
"primary, secondary and tertiary" exist because "most design systems have that". Stick to what
you observed.

---

## Layer 4 — Layout and composition

**Guiding question:** *How is space organized?*

### What to identify

- **Inferable grid**: 12 columns? 16? Other? Detectable container max-width?
- **Inferable breakpoints**: if the material shows only desktop, note that. If there are
  responsive versions, detect breakpoints.
- **Vertical rhythm**: is there consistent spacing between sections?
- **Visual hierarchy**: how are primaries vs secondaries established? (size, weight, color,
  position, space)
- **Composition patterns**: hero, feature-grid, alternating sections, card list, sidebar
  layout, centered single-column, etc.
- **Density per zone**: are there dense zones (dashboards, tables) and spacious zones (heroes,
  marketing sections)?

### Common trap

Don't confuse "centered" with "good layout". Note real decisions: does it use asymmetric
whitespace? Does it align to baseline? Does it have a clear focal point?

---

## Layer 5 — Reconstruction

**Guiding question:** *If you had to rebuild it, what would you need?*

This layer is **prescriptive**, not descriptive. You're talking to a human or AI who will
build something similar.

### Sub-sections

**5.1 Suggested stack**
- Vanilla HTML/CSS? Tailwind? Tailwind + shadcn/ui? Material UI? Something more exotic?
- Justify with evidence: if you saw classes like `flex items-center gap-4`, it's Tailwind. If
  you saw `MuiButton-root`, it's MUI. If there are no clues, suggest Tailwind as a reasonable
  default.

**5.2 Quick wins (easy to replicate)**
- Things that with basic tokens and components come out the same
- Example: "Palette and typography are direct. Buttons with `bg-blue-600 rounded-md px-4 py-2`
  cover the pattern."

**5.3 Tricky bits (what needs care)**
- Animations, transitions, effects not visible in static but seemingly present
- Custom typefaces that require licensing
- Non-trivial layouts (masonry, asymmetric grid)
- States you didn't see but logically exist (hover, loading, empty)

**5.4 Responsive coverage gotcha**
- If you only have desktop material, **say so explicitly** in Open Questions and recommend
  the user rerun with `python scripts/capture_site.py <URL> --viewports desktop,tablet,mobile`
  before committing to breakpoint assumptions.
- Marketing landings often have very different mobile structures (sticky CTAs, collapsed nav,
  reordered sections) that you cannot infer from desktop alone.

**5.5 Confidence map**
General summary of how confident you are in each layer:

| Layer | Confidence | Why |
|---|---|---|
| Identity | ✅ high | Clear material |
| Tokens — colors | ✅ high | Hex extracted directly |
| Tokens — typography | ⚠️ medium | Family identified but partial weights |
| Components | ⚠️ medium | Only saw 3 of a probably larger catalog |
| Layout | ❓ low | Only desktop material, no responsive info |

---

## How to use all this

It's not a mechanical checklist. It's a **scaffold** so the analysis doesn't stay shallow. You
pass through the 5 layers in order, giving more depth to those the material supports and to
the emphasis the user requested.

If the user said "I want mood/reference", Layer 1 weighs more. If they said "extract tokens",
Layer 2. If they said "reconstruction", Layer 5. But **all layers are covered**, even briefly.
