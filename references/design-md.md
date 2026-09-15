# design.md: how to analyze and what to write

One reference for Steps 3 and 4: the six analysis layers, token rigor, and the output
contract. Every section of the design.md below says what to look for, how to judge it and
how long to write it.

## Depth

- **Standard (default).** Every section present, written to the length caps below. This is
  what a downstream agent needs to rebuild the design.
- **Deep.** Only when the user asks for it ("deep", "exhaustive", "full brand book",
  "document everything") or the emphasis is mood/reference, where Section 1 goes deep and
  Sections 2-3 stay standard. Caps double and prose can run to 2-3 paragraphs.

Length is not quality. A capped section that is specific beats a long one that is generic.

## Honesty rules (all depths)

- Every important inference carries a marker: ✅ high (seen directly), ⚠️ medium
  (well-grounded inference), ❓ low (speculation, said openly).
- Real values only: `#3B82F6`, `16px`, `GeistSans`. Never "sky blue" or "medium size".
- Report what you observed. One button seen is "1 variant observed", not "primary,
  secondary, tertiary". A short honest system beats a long invented one.
- No framework claims without evidence (`bg-blue-500` classes → Tailwind; `MuiButton-root`
  → MUI). No evidence → say "no framework signal" and suggest a default.
- "Modern and clean" is not analysis. Name what makes it look that way.

## Token rigor

- **A token is a repeated, named decision.** Seen once is a value; seen 3+ times is
  probably a token. CSS custom properties and computed styles are ✅ by default; values
  read from pixels are ⚠️ at best (`extract_colors.py` grounds image hex codes).
- **Semantic roles, not numbers:** `primary` (CTAs, primary links), `surface` /
  `surface-elevated` (page / card backgrounds), `text-primary` / `text-muted`, `border`,
  `accent`, `success` / `warning` / `error`. Keep numeric scales (50-900 or 100-1000) as
  scales when the source has them.
- **Typography:** family from CSS or computed styles is ✅; recognized visually is ⚠️
  ("looks like Inter"); unrecognized is described ("geometric sans, open apertures").
  Report only the sizes and weights you saw. Negative tracking on display type and tight
  heading line-height (1.1-1.2) are deliberate signals.
- **Spacing:** infer the base unit from distances (multiples of 4 or 8) and list only the
  multiples observed.
- **Radii and elevation:** list observed values; note whether radii are single, tiered
  (buttons < cards) or deliberately mixed.

## The frontmatter

The YAML frontmatter is the single source of token values. The body references it as
`{group.name}` followed by the literal value, e.g. `{colors.primary}` (#171717), and
`build_tokens_json.py` exports it to DTCG. Any top-level map is a valid group.

```yaml
---
version: anydesign-1
name: Example
source: https://example.com
captured_at: YYYY-MM-DD
description: |
  2-3 sentences of brand atmosphere an agent reads before the rest.
colors:
  primary: "#171717"
  surface: "#FFFFFF"
  text-primary: "#171717"
  text-muted: "#4D4D4D"
  border: "#EBEBEB"
typography:
  display: { fontFamily: "Geist, sans-serif", fontSize: 48px, fontWeight: 600, letterSpacing: -0.02em }
  body: { fontFamily: "Geist, sans-serif", fontSize: 16px, fontWeight: 400, lineHeight: 1.5 }
spacing:
  base: 4px
  scale: [4, 8, 12, 16, 24, 32, 48, 64]
rounded:
  sm: 6px
  lg: 12px
shadows:              # optional
  card: "0 1px 2px rgba(0,0,0,0.04)"
components:
  button-primary: { backgroundColor: "{colors.primary}", textColor: "{colors.surface}", rounded: "{rounded.sm}", padding: 10px 24px }
---
```

Role names for typography (`display`, `body`, `caption-mono`), not HTML tags. Every key under
`components` gets a Section 3 heading with **exactly that key**: `#### button-primary`.

## The body

Section numbers and headings are fixed: `lint_design_md.py` reads them.

```markdown
# Design Analysis: <name>

> Analysis generated with the `anydesign` skill. Date: YYYY-MM-DD. Emphasis: <reconstruction | mood | design system | mixed>

## Source
## TL;DR
## 1. Visual identity
### 1.1 Surface description
### 1.2 Brand voice / Atmosphere
### 1.3 The "ONE brand thing"
## 2. Design System (tokens)
### 2.1 Colors
### 2.2 Typography
### 2.3 Spacing
### 2.4 Radii
### 2.5 Elevation system
### 2.6 Borders
### 2.7 Accessibility quick-check
## 3. Components Inventory
### 3.1 Generic components
### 3.2 Signature components
## 4. Layout & Composition
### 4.1 Grid & containers
### 4.2 Composition patterns
### 4.3 Responsive behavior
### 4.4 Image behavior
## 5. Reconstruction Notes
## 6. Do's and Don'ts
### Do
### Don't
## 7. Open Questions
## 8. Companion files
```

### Source and TL;DR

Source: type, URL or path, capture method (e.g. "CSS vars digest + Playwright computed
styles and frames"), limitations ("desktop and mobile only"). TL;DR: 2-3 sentences with
personality, what is distinctive and one actionable insight.

### 1. Visual identity (guiding question: what does this design want to be?)

**1.1 Surface description.** Five labeled lines: Personality (3-5 adjectives), Mood,
Stylistic references ("Linear-like"), Information density, Implicit positioning. Each
backed by an observation. Confidence marker.

**1.2 Brand voice.** What the design *believes* about its audience, such that every
aesthetic choice follows. Not copywriting ("approachable yet premium"). Test: would a
careful viewer say "yes, and now I see why every choice follows"? If it could describe any
tech company, rewrite. Example: Vercel, "Engineering quietude. The surface is restrained
because the platform IS the product; marketing must not dilute what infrastructure
promises." Standard: one paragraph, at most 90 words.

**1.3 The ONE brand thing.** The element that would still say "this is X" if everything
else went generic: a single chromatic moment, a typographic gesture, a geometric move, or a
decoration scoping rule. Four one-line bullets: the thing (concrete hex / typeface /
asset), why it carries the brand, how the rest is restrained around it, where it appears
and where it deliberately doesn't. No ONE thing (neutral admin UI)? Say so.

### 2. Design System (guiding question: which decisions repeat?)

- **2.1 Colors:** table `Token | Hex | Role | Where it appears | Confidence`, first cell
  `` `name` `` matching the frontmatter key. Standard: up to 12 rows; full scales live in
  the frontmatter. Dark mode seen → second table.
- **2.2 Typography:** detected family with confidence, fallback, table
  `Token | Size | Weight | Line-height | Use`, notable tracking.
- **2.3 Spacing:** base unit, observed multiples, consistency marker.
- **2.4 Radii:** observed values and the system behind them.
- **2.5 Elevation:** tiers Level 0-N as a table `Level | Name | Treatment | Use`, plus the
  philosophy (stacked small shadows, single drop, inset-border-as-elevation, flat, surface
  tone instead of shadow). One or two tiers is a valid answer. Then *decorative depth* if
  present: polarity-flipped light/dark bands, scoped atmospheric gradients, background
  patterns.
- **2.6 Borders:** width, color, focus treatment.
- **2.7 Accessibility:** with 2+ text/surface pairs, run `check_contrast.py --output
  design-a11y.md` and quote its summary lines. Fewer pairs → omit and say why.

### 3. Components (guiding question: which reusable pieces form it?)

**3.1 Generic components** (buttons, inputs, cards, nav, badges, modals): one `####` per
frontmatter component key, with Variants, Sizes, Visible states, Padding/Radius and
Confidence. Standard: up to 6 components, 5 short bullets each. Computed styles give
exact values; use them.

**3.2 Signature components:** patterns unique to this brand (Linear's command palette,
Stripe's gradient code card). What it is, why it's signature, how it's composed, where it
appears. Up to 3. None → "No signature components detected; system uses standard UI
primitives."

### 4. Layout (guiding question: how is space organized?)

- **4.1 Grid & containers:** max width, gutters, vertical rhythm between sections, how
  hierarchy is set (size, weight, color, space).
- **4.2 Composition patterns:** named patterns (centered hero, split hero, feature grid,
  alternating bands, dense footer matrix).
- **4.3 Responsive:** breakpoints table only with rows the material supports (desktop only
  → mark ❓ and recommend `--viewports desktop,tablet,mobile`); touch targets against 44px;
  collapsing strategy per pattern ("3-up → 2-up → 1-up"). `clamp()` values mean fluid type.
- **4.4 Image behavior:** one bullet per image kind seen (decorative gradient, logo strip,
  product mockups, photography, icon set with stroke/fill). No images → say so.

### 5. Reconstruction Notes (prescriptive: talking to whoever rebuilds it)

Suggested stack with the evidence (2 lines). Quick wins (up to 3). Tricky bits (up to 4:
animations, licensed fonts, unusual layouts). Implicit states to define, in one line
(hover, focus, loading, empty, error). Confidence map table `Layer | Confidence | Why`.

### 6. Do's and Don'ts (what an agent extending this must be told)

Each rule is specific to this design, cites a token and traces to an observation.
"Use primary for CTAs" is generic and useless; "Reserve `{colors.primary}` (#171717) for
the conversion target, never as a card background" is a rule. Draw from color discipline
(reserved colors, accent count), typography (weight ceiling, case, mono scope), elevation,
radius scales that must not mix, spacing rhythm, decoration scoping. Standard: 5 Do and 5
Don't, one line each. Fewer than 3 grounded rules each → write "Insufficient evidence to
derive brand-specific usage rules" instead of padding.

### 7. Open Questions

Bullets of what could not be determined and what material would settle it. None →
"Material sufficient for complete reconstruction."

### 8. Companion files

One line each: `design-tokens.json` (list it as generated: you run `build_tokens_json.py`
right after lint), `design-a11y.md` if generated, capture frames used.

## Before writing: art direction QA pass

Run this pass in your head after the layers and before writing. Do not write the checklist
into the design.md; fold what you find into the right section, and put present patterns
that constrain future work into Section 6. Mention an absence only when it is diagnostic
("no shadows: flat by design"). Ambiguous → Section 7.

- **Surface rhythm:** light/dark section bands; a gradient scoped to one zone; density
  swinging between spacious heroes and dense matrices.
- **Token coexistence:** two radius scales kept in separate contexts (6px controls vs pill
  CTAs); mono reserved for code or also used for labels; a display weight ceiling;
  a tracking convention.
- **Color discipline:** exactly one chromatic moment in a neutral palette (often the ONE
  thing); a parallel alpha scale; feedback colors kept out of decoration.
- **Elevation discipline:** stacked vs single-drop shadows; inset 1px shadow used as border;
  surface tone instead of shadow.
- **Composition:** split vs centered hero as the canonical one; deliberate asymmetric
  whitespace; consistent image treatment.
