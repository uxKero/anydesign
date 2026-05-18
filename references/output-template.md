# Output Template — The design.md template

This is the **base** template of the `design.md` file the skill generates. Use it as the output
contract. Adapt the depth of each section based on the user's emphasis (reconstruction / mood /
system), but **don't remove sections** unless explicitly empty due to lack of info — in which
case, say so.

---

## Template

```markdown
# Design Analysis — [Site / file / reference name]

> Analysis generated with the `anydesign` skill.
> Date: YYYY-MM-DD
> Analysis emphasis: [reconstruction | mood | design system | mixed]

---

## Source

- **Source type**: [local image | URL | Figma | combination]
- **Path / URL**: `<the concrete source>`
- **Capture method**: [direct vision | HTML via WebFetch + CSS vars extraction | Playwright multi-viewport screenshot | Figma MCP]
- **Detected limitations**: [if any, e.g., "only desktop material visible, no responsive"]

---

## TL;DR

[2-3 sentences. Visual personality + what's distinctive + one actionable insight.]

*Example: Clinical productivity-oriented design, in the aesthetic line of Linear/Vercel.
Restricted palette in cool neutrals with a single blue accent (#3B82F6). Geometric sans
typography with negative tracking on headings, suggesting Inter or Geist.*

---

## 1. Visual identity

**Personality** (3-5 adjectives): [adjectives]

**Mood**: [what emotion it conveys, briefly]

**Detectable stylistic references**: [if you recognize patterns, e.g., "Linear-like aesthetic",
"current web brutalism", "Apple homepage editorial"]

**Information density**: [minimalist | balanced | dense | saturated]

**Implicit positioning**: [who this design speaks to — devs, enterprise, creatives, etc.]

**Confidence**: [✅ high | ⚠️ medium | ❓ low]

---

## 2. Design System (tokens)

### 2.1 Colors

| Token | Hex | Role | Where it appears | Confidence |
|---|---|---|---|---|
| `primary` | `#3B82F6` | Main action, links | CTA buttons, nav links | ✅ high |
| `surface` | `#FFFFFF` | Base background | Body | ✅ high |
| `text-primary` | `#111827` | Main text | Body, headings | ✅ high |
| `text-muted` | `#6B7280` | Secondary text | Captions, labels | ⚠️ medium |
| ... | | | | |

[If dark mode exists, add equivalent table below.]

### 2.2 Typography

- **Detected family**: `[Inter | Geist | etc.]` *(confidence: ⚠️ medium — visually inferred)*
- **Suggested fallback**: `system-ui, sans-serif`

**Observed scale:**

| Token | Size | Weight | Line-height | Use |
|---|---|---|---|---|
| `display` | 64px | 600 | 1.1 | Hero title |
| `h1` | 48px | 600 | 1.15 | Section titles |
| `h2` | 32px | 600 | 1.2 | Subsection |
| `body` | 16px | 400 | 1.6 | Main text |
| `body-sm` | 14px | 400 | 1.5 | Captions, metadata |

**Notable tracking**: -0.02em on display and h1 (typographic care signal)

### 2.3 Spacing

- **Inferred base unit**: 4px (Tailwind-like scale)
- **Observable multiples**: 4, 8, 12, 16, 24, 32, 48, 64, 96
- **Consistency**: ✅ high — systematic pattern

### 2.4 Radii

- `sm`: 6px (buttons, inputs)
- `md`: 12px (cards)
- `full`: 9999px (avatars, badges)

### 2.5 Shadows

- `shadow-sm`: visible on cards on hover, subtle
- `shadow-md`: on modals and elevated elements
*[Or "No shadows detected — flat design" if applicable.]*

### 2.6 Borders

- Base color: `#E5E7EB` (light gray)
- Thickness: 1px
- Focus states: 2px ring in `primary` with opacity

---

## 3. Components Inventory

### Button
- **Variants**: primary (bg-primary), ghost (transparent + border)
- **Observed sizes**: md (40px tall)
- **Visible states**: default
- **Padding**: ~24px horizontal, 10px vertical
- **Radius**: 6px
- **Confidence**: ✅ high

### Input
- **Variants**: single text
- **Visible states**: empty, focus
- **Border**: 1px solid border, primary focus ring
- **Confidence**: ⚠️ medium — only saw one case

### Card
[...continue with each observed component]

---

## 4. Layout & Composition

- **Inferable grid**: container max-width ~1280px, horizontal padding 24px on desktop
- **Inferable breakpoints**: [if responsive info exists, list it; if not, say "only desktop
  material visible"]
- **Vertical rhythm**: sections separated by ~96px
- **Observed composition patterns**: centered hero, 3-column feature grid, dense footer
- **Visual hierarchy**: established by typographic size and color contrast (not by
  oversaturated color)

---

## 5. Reconstruction Notes

### Suggested stack

**[Tailwind | Tailwind + shadcn/ui | vanilla CSS | other]**

Justification: [why — observed classes, recognized patterns, simplicity of the case]

### Quick wins

- [What's direct to replicate with basic tokens]
- [Example: palette and typography cover 80% of the look]

### Tricky bits

- [What needs special care]
- [Animations, custom fonts, non-trivial layouts, invisible states]

### Implicit states to define

Probably exist but weren't captured — define before implementing:
- Button hover states
- Visible focus
- Loading states
- Empty states
- Input error states

### Confidence map

| Layer | Confidence | Why |
|---|---|---|
| Identity | ✅ high | Sufficient material, clear patterns |
| Colors | ✅ high | Hex extracted directly |
| Typography | ⚠️ medium | Family visually inferred |
| Spacing | ✅ high | Verifiable consistent pattern |
| Components | ⚠️ medium | Partial catalog observed |
| Layout | ❓ low | Only desktop material |

---

## 6. Open Questions

[List of things you COULDN'T determine that need user input or more material]

- Does the site have dark mode? Saw no indications.
- Are there Button variants besides primary and ghost?
- Is the typography Inter or Geist? Need to see CSS to confirm.
- What are the exact breakpoints? Only saw desktop.

*If no open questions, justify it: "Material sufficient for complete reconstruction."*

---

## 7. Companion files

- [ ] `design-tokens.json` — structured tokens in W3C DTCG format (`$value`/`$type`),
      ready for Style Dictionary, Figma Variables, Tokens Studio
- [ ] `design-a11y.md` — WCAG 2.1 contrast report for the extracted color pairs
      (emit when at least two colors with clear text/surface relationships were captured)
- [ ] `design-screenshot.png` — capture used (if generated by Playwright or MCP);
      `-desktop` / `-tablet` / `-mobile` suffixes when multi-viewport

---

*End of analysis. If you want to deepen any section, convert this into a prompt for Claude
Code, or analyze another source to compare, let me know.*
```

---

## Notes for filling the template

### Adaptation based on emphasis

- **If emphasis = reconstruction** → Section 5 more detailed, Section 1 briefer
- **If emphasis = mood/reference** → Section 1 more detailed with rich vocabulary, Sections 2-3
  briefer
- **If emphasis = design system** → Sections 2-3 very detailed, plus always generate
  `design-tokens.json`

### Confidence marker rules

- ✅ high: directly seen, without significant inference
- ⚠️ medium: well-grounded inference but could be wrong
- ❓ low: reasonable speculation, say so openly

### What's never missing

1. **Source** with complete source info
2. **TL;DR** of 2-3 sentences
3. **Confidence map** at the end of Reconstruction Notes
4. **Open Questions** (or justification of their absence)

### What can be missing

- Token sub-sections if the source doesn't support them (e.g., static image without detectable
  typography info → omit the weights sub-section)
- Components Inventory if the source only shows layout without clear components
- Shadows if there are none
