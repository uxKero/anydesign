# Capture Flows — How to capture each source type

This reference defines the technical capture flow for each input type. Consult it when you start
Step 2 of the main workflow.

---

## Flow 1 — Local image

**Typical input:** the user uploads a PNG/JPG/WebP, or passes a path like
`/mnt/user-data/uploads/ref.png`.

**What to do:**
1. The image is already available via multimodal vision. **No script needed.**
2. If the path is in `/mnt/user-data/uploads/`, you can reference it directly.
3. If you need pixel-precise hex codes for the dominant colors (vision is approximating),
   run `python scripts/extract_colors.py <image-path>` — it returns dominant colors with area
   percentages.
4. Move to Step 3 (analysis).

**When to ask for more:**
- If the image is too small or low-resolution → ask the user for a better version before
  analyzing (analysis will be poor and you'll end up inventing tokens).
- If the image shows only part of something (e.g., only the header) → ask if they have
  captures of other sections for fuller vision.

---

## Flow 2 — Website URL

**Typical input:** a URL pasted by the user.

**Strategy: scripts first, and only their digests enter the context.** Raw HTML of a
marketing site is 200k to 570k tokens, and its full CSS variable dump 15k to 55k. Neither
is ever read whole.

### Step 2.1: explicit tokens from CSS custom properties

```bash
python scripts/extract_css_vars.py <URL>
```

Fetches the HTML, every linked stylesheet and inline `<style>` block, and prints a digest:
numeric scales collapsed to one line each (`--ds-gray-*: 100=#f2f2f2 200=#ebebeb ...`),
`var()` aliases resolved to their final value, theme redefinitions flagged, framework
plumbing (`--tw-*` and similar) hidden, capped at `--budget` characters (default 6000,
about 2-3k tokens). The full JSON goes to `./css-vars.json`. When a value you need is
not in the digest, search it without refetching and without writing code:

```bash
python scripts/extract_css_vars.py --grep 'border|radius|shadow'
```

**What to do with the extracted variables:**
- They are the site's **explicit token system**: mark them ✅ high confidence in
  Section 2, and cite the stylesheet source in the Source section.
- Map them to semantic roles (`--ds-gray-1000` → `text-primary`) in the frontmatter.

### Step 2.2: rendered styles and frames

```bash
python scripts/capture_site.py <URL> --viewports desktop,mobile
```

Renders the page in headless Chromium, dismisses common cookie banners, then:

1. **Prints computed styles** of body, h1-h3, paragraphs, links, buttons, inputs, header
   and cards: font family, size, weight, line-height, letter-spacing, color, background,
   radius, padding, border and shadow, read from the live DOM. These are real values:
   they give typography and component tokens without reading any HTML.
2. **Saves up to 4 viewport-sized frames per viewport**, spread from top to bottom
   (`capture-desktop-01.png` ... `capture-mobile-04.png`). Scrolling to each frame also
   triggers lazy content.

Read only the frames you need: normally the first desktop frame for identity and hero,
one or two more for sections and components, and one mobile frame for responsive notes.
**Never write your own capture or scroll scripts.** Options that cover the usual needs:

- `--frames 2` or `--frames 6`: fewer or more frames
- `--viewports desktop,tablet,mobile`: responsive analysis (Layer 4)
- `--full-page`: the old single tall PNG; unreadable once downscaled on long pages
- `--save-html`: keep the rendered HTML to `grep` for class names (framework signals)
- `--selector "header.navbar"`: element mode, see below

**Element capture** (element mode only, see `references/element-copy.md`):

```bash
python scripts/capture_site.py <URL> --selector "header.navbar" --output ./element.png
```

Screenshots only the first matching element's bounding box and saves its outerHTML.

**Important user warning:** the first time Playwright runs, it downloads ~300MB of
Chromium. Warn them so they're not surprised.

### Step 2.3: without Playwright

If Playwright is not installed and the user doesn't want to install it, use `WebFetch`
on the URL for content, structure and brand meta (`og:image`, `theme-color`), together
with the Step 2.1 digest for tokens. Mark typography and component measurements ⚠️
medium, since they were not read from rendered styles. For framework signals, look at
class names in what `WebFetch` returns: `bg-blue-500` (Tailwind), `MuiButton-root`
(Material UI), `chakra-button` (Chakra), `ant-btn` (Ant Design).

---

## Flow 3 — Figma link

**Typical input:** a URL like `https://www.figma.com/file/<key>/...` or
`https://www.figma.com/design/<key>/...` or a specific node with `?node-id=...`.

**Prerequisite:** the user must have the Figma MCP connected. If not, tell them they need to
connect it from the Claude app before continuing.

### Step 3.1 — Identify the scope

- **Full file URL** → you'll analyze the entire file. This can be huge. Suggest the user pass
  a link to a specific frame/page.
- **URL with `node-id`** → already scoped. Better.

### Step 3.2 — MCP tools in order

1. **`get_metadata`** → first, to understand the structure of the file/node (what's inside,
   what element types, hierarchy). Orients you before requesting heavy content.

2. **`get_variable_defs`** → if the file uses Figma Variables (colors, spacing, typography),
   you have them explicit here. **This is gold:** they're the design system tokens already
   structured by the designer. No need to infer them.

3. **`get_design_context`** → detailed content of the node. Returns components, properties,
   values. Richest but also most token-expensive. Request it after having the overview.

4. **`get_screenshot`** → if you need visual reference besides structure (useful for Layer 1
   "Identity" — mood, personality).

### Step 3.3 — Advantage of the Figma flow

When the file is well-structured, **tokens come served**. Your role shifts: instead of
inferring from pixels, you **document** what the designer already defined and add layers of
interpretation (mood, implicit components, system decisions).

Mark this in the `design.md`: tokens with ✅ high confidence are those that came from
`get_variable_defs`, not those you inferred yourself.

---

## Flow 4 — Combinations

**Common case:** the user passes a URL **and** a manual screenshot of a specific state
(e.g., "the site rendered on mobile" or "the modal open").

Combine them like this:
- **CSS vars digest + computed styles** → explicit tokens, real typography and component values
- **Screenshot** → visual presentation, real rendered colors, final layout
- In the `design.md`, "Source" section, cite both sources and clarify what each contributed

**Less common but valid case:** Figma + production site. Useful to audit whether the site
implemented what the design defined. In this case the `design.md` can have an extra section on
**design-vs-implementation discrepancies**.

---

## Error handling

| Error | What to do |
|---|---|
| URL returns 403/404 | Tell the user, offer alternatives (manual screenshot, archive.org) |
| URL blocked by Cloudflare/captcha | Tell them honestly. **Don't attempt bypass.** Request manual screenshot. |
| Playwright not installed | Give the install command. Don't attempt workaround. |
| Figma MCP can't access file | Verify the file is accessible to the logged-in user. |
| Cookie banner blocks content even after auto-dismiss | Ask the user for a manual screenshot with the banner already closed. |
| Corrupt or unreadable image | Ask for a new version. |

**Principle:** honesty about limitations is part of being professional. An invented analysis is
worse than an analysis with missing but clear data.
