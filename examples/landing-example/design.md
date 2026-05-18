# Design Analysis — Lumen Notes (fictional)

> Analysis generated with the `anydesign` skill.
> Date: 2026-05-18
> Analysis emphasis: reconstruction + design system

---

## Source

- **Source type**: URL
- **Path / URL**: `https://lumen.example/` *(fictional, for documentation purposes)*
- **Capture method**: HTML via `WebFetch` + CSS custom properties via
  `scripts/extract_css_vars.py`
- **Detected limitations**: only desktop layout observed; no dark mode toggle visible in
  the captured HTML; mobile breakpoints not exercised

---

## TL;DR

Clinical, developer-oriented landing in the Linear/Vercel aesthetic family. Cool neutral
palette anchored on a deep slate background (`#0F172A`) with a single emerald accent
(`#10B981`); generous spacing on an 8px grid; geometric sans (Inter declared in CSS). The
22 extracted CSS custom properties give a high-confidence token map ready for
reconstruction.

---

## 1. Visual identity

**Personality** (3-5 adjectives): clinical, calm, developer-targeted, restrained,
typographically-led

**Mood**: confident and quiet — not shouting, not playful. Reads as a tool, not a
consumer app.

**Detectable stylistic references**: strong Linear/Vercel/Anthropic-homepage family.
Dark surface with a single bright accent and lots of whitespace.

**Information density**: minimalist — the hero uses ~60% whitespace.

**Implicit positioning**: developers and technical knowledge workers. The accent is a
"command-line green" rather than a marketing blue.

**Confidence**: ✅ high — consistent signals across hero, features, and footer.

---

## 2. Design System (tokens)

All values below were extracted from the site's CSS custom properties via
`scripts/extract_css_vars.py`. They are explicit tokens defined by the authors —
**not** inferred — and therefore carry ✅ high confidence by default.

### 2.1 Colors

| Token | Hex | Role | Where it appears | Confidence |
|---|---|---|---|---|
| `--color-bg` | `#0F172A` | Surface — base background | Body | ✅ high |
| `--color-surface-elevated` | `#1E293B` | Cards, feature blocks | Feature grid | ✅ high |
| `--color-text-primary` | `#F8FAFC` | Body text on dark | Body, headings | ✅ high |
| `--color-text-muted` | `#94A3B8` | Captions, metadata | Eyebrow text, labels | ✅ high |
| `--color-text-subtle` | `#64748B` | De-emphasized text | Footer links | ✅ high |
| `--color-border` | `#334155` | Subtle borders | Card outlines, dividers | ✅ high |
| `--color-border-strong` | `#475569` | Focus rings, emphasis | Input focus | ✅ high |
| `--color-accent` | `#10B981` | Primary CTA, accents | "Start free" button, logo | ✅ high |
| `--color-accent-hover` | `#059669` | CTA hover state | Hover on accent | ✅ high |
| `--color-success` | `#22C55E` | Feedback | Success badges | ✅ high |
| `--color-warning` | `#F59E0B` | Feedback | Warning badges | ✅ high |
| `--color-danger` | `#EF4444` | Feedback | Error badges | ✅ high |

### 2.2 Typography

- **Declared family**: `Inter, ui-sans-serif, system-ui, sans-serif` *(confidence: ✅ high — declared in CSS)*
- **Fallback chain**: `ui-sans-serif, system-ui, sans-serif`

**Observed scale:**

| Token | Size | Weight | Line-height | Use |
|---|---|---|---|---|
| `--font-size-display` | 60px | 600 | 1.1 | Hero title |
| `--font-size-h2` | 32px | 600 | 1.2 | Section titles |
| `--font-size-body` | 16px | 400 | 1.6 | Main text |

**Notable tracking**: `-0.02em` declared on display (typographic care signal).
**Weights used**: 400, 500, 600.

### 2.3 Spacing

- **Inferred base unit**: 4px (Tailwind-like scale; multiples observed: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128)
- **Declared tokens**: `--space-1` through `--space-16`
- **Consistency**: ✅ high — every margin/padding observed maps to a declared step

### 2.4 Radii

- `--radius-sm`: 6px (buttons, inputs, badges)
- `--radius-md`: 16px (cards) — Tailwind's `rounded-2xl` value, confirmed in CSS

### 2.5 Shadows

- No shadow tokens declared in CSS. The dark surface establishes hierarchy via
  background elevation (`--color-bg` → `--color-surface-elevated`) rather than shadow.
- **Confidence**: ⚠️ medium — there could be inline shadows on hover states not visible
  in the static capture.

### 2.6 Borders

- Default thickness: 1px
- Color: `--color-border` (`#334155`)
- Focus state: 2px ring in `--color-border-strong`

### 2.7 Accessibility quick-check

See companion `design-a11y.md`. Summary:
- `text-primary` on `bg`: **17.06:1** — AAA ✅
- `text-muted` on `bg`: **6.96:1** — AA ✅, AAA large ✅ (just under AAA normal)
- `accent` on `bg`: **7.04:1** — AAA ✅
- `text-primary` on `accent` (anti-pattern): **2.42:1** — fails all. **Do not place white text on the accent button** — the implementation correctly puts `bg` (dark) on `accent` (7.04:1 ✅).

---

## 3. Components Inventory

### Button
- **Variants**: primary (solid accent), ghost (transparent + border-strong)
- **Sizes**: md (40px tall)
- **Visible states**: default, hover (color shift via `--color-accent-hover`)
- **Padding**: 24px horizontal, 10px vertical
- **Radius**: 6px (`--radius-sm`)
- **Confidence**: ✅ high

### Card
- **Variants**: single — feature card with icon + title + body
- **Background**: `--color-surface-elevated`
- **Border**: 1px solid `--color-border`
- **Radius**: 16px (`--radius-md`)
- **Padding**: 32px
- **Confidence**: ✅ high

### Input
- **Variants**: single text input (email signup in footer)
- **Visible states**: empty, focus (2px ring in `--color-border-strong`)
- **Border**: 1px solid `--color-border`
- **Confidence**: ⚠️ medium — only one input observed

### Badge
- **Variants**: success, warning, danger
- **Style**: pill (`--radius-sm`), solid background of the relevant semantic color
- **Confidence**: ⚠️ medium — observed in component examples, not in active marketing copy

---

## 4. Layout & Composition

- **Container max-width**: ~1200px, horizontal padding 24px on desktop
- **Inferable breakpoints**: ❓ low — only desktop observed; CSS does declare a `--breakpoint-md` token suggesting a 768px breakpoint exists
- **Vertical rhythm**: sections separated by ~96px (`--space-16` × 1.5)
- **Composition patterns**: centered hero, 3-column feature grid, footer with sitemap + email capture
- **Visual hierarchy**: established by typographic size + color contrast (white on dark) rather than oversaturated color

---

## 5. Reconstruction Notes

### Suggested stack

**Tailwind + a custom Tailwind config that mirrors the extracted tokens.**

Justification: the CSS class names visible in the HTML (`bg-slate-900`, `text-zinc-100`,
`rounded-2xl`) are direct Tailwind utilities. Wire the extracted custom properties into
`tailwind.config.js` (Tailwind v4 reads CSS variables natively).

### Quick wins

- Palette and typography cover ~80% of the look. Drop the CSS variables into a `:root`
  block, set Inter via `next/font` or `<link>`, and the surface is immediately faithful.
- Buttons with `bg-emerald-500 text-slate-900 rounded-md px-6 py-2.5` reproduce the
  primary CTA.

### Tricky bits

- Whatever interaction / motion exists is not visible in static capture. Expect to design
  micro-interactions from scratch (subtle scale or color transitions on hover).
- The single accent color does heavy lifting — design hover/disabled/focus states
  carefully to avoid breaking the calm.
- Card hover state was not observed; the design likely has one. Define before shipping.

### Responsive coverage gotcha

Only the desktop layout was modeled. Before committing breakpoint assumptions, capture
the site at mobile and tablet viewports:

```bash
python scripts/capture_site.py https://lumen.example/ \
    --viewports desktop,tablet,mobile
```

### Implicit states to define

- Button hover (visible)
- Button disabled
- Card hover
- Input error
- Form submission loading
- Empty states for the feature grid (if it ever has zero items)

### Confidence map

| Layer | Confidence | Why |
|---|---|---|
| Identity | ✅ high | Clear signals, consistent palette |
| Colors | ✅ high | Extracted from CSS variables, not inferred |
| Typography | ✅ high | Family declared in CSS, scale declared in CSS |
| Spacing | ✅ high | Token scale declared in CSS |
| Components | ⚠️ medium | Only 4 components observed in source |
| Layout | ❓ low | Only desktop captured |

---

## 6. Open Questions

- Does the product have a dark/light mode toggle? Only dark was observed; no
  `prefers-color-scheme` rules in the captured CSS.
- Are there Button variants beyond primary and ghost (e.g., destructive)?
- What's the mobile navigation pattern (hamburger? bottom sheet?)
- Is there a documented motion system, or are transitions ad-hoc?
- The CSS declares `--breakpoint-md` and `--breakpoint-lg` but no rules were observed
  using them in the capture — confirm whether they're used elsewhere.

---

## 7. Companion files

- [x] `design-tokens.json` — structured tokens in W3C DTCG format
      (`$value`/`$type`), ready for Style Dictionary / Figma Variables / Tokens Studio
- [x] `design-a11y.md` — WCAG 2.1 contrast report for the four key text/surface
      combinations
- [ ] No screenshot bundled — HTML+CSS extraction was sufficient

---

*End of analysis. If you want to deepen any section, convert this into a prompt for Claude
Code, or analyze another source to compare, let me know.*
