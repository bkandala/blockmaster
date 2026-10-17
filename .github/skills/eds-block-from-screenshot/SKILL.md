---
name: eds-block-from-screenshot
description: Build an Adobe Edge Delivery Services (EDS / aem.live / Franklin / Helix) block for an aem-boilerplate repo from a screenshot or URL of a page section — block JS and CSS, responsive layout and variants, a da.live content model, and a sample page rendered and compared against the reference. Use this whenever someone shares a screenshot, mockup, Figma export or webpage link and wants it as an EDS block, asks to "recreate", "rebuild", "port" or "make a block like" a section, or is migrating AEM components to Edge Delivery, even if they don't say "block".
---

# EDS block from a screenshot

Turn a picture (or live URL) of one page section into a production-quality
block for a plain `adobe/aem-boilerplate` repo, plus everything an author
needs to use it in da.live.

What you deliver, all inside the user's repo:

| File | Purpose |
|---|---|
| `blocks/<name>/<name>.js` | `export default function decorate(block)` |
| `blocks/<name>/<name>.css` | scoped, mobile-first styles |
| `blocks/<name>/README.md` | content model for authors (not served: `*.md` is in `.hlxignore`) |
| `drafts/<name>.plain.html` | sample page: local preview + da.live upload |
| `drafts/media/*` | placeholder images for the sample |

The point of the content model and sample page is that a block nobody can
author is useless. Spend real thought on the authoring shape — it outlives the
CSS.

## Inputs

- **Reference**: a screenshot of the section, a URL (plus which section), or both.
- **Repo**: the path of an aem-boilerplate checkout. If none was given, ask for
  it. Confirm it looks like one (`scripts/aem.js`, `blocks/`, `head.html`).
  Read the repo's `AGENTS.md`/`CLAUDE.md` if present — they override the
  defaults here.

If the screenshot clearly holds several sections, ask which one to build, or
whether to build each (one block per distinct section; plain heading-and-text
areas are default content, not blocks).

## Workflow

### 1. Study the reference

Write a short analysis before touching code — it's what you'll check the
render against later:

- **Structure**: the repeated unit (if any), how many, and what's inside each
  (image, eyebrow, heading, body, CTA, icon, stat).
- **Layout per breakpoint**: what the screenshot shows, and your inference for
  the widths it doesn't show (usually: multi-column on desktop → 2 columns on
  tablet → stacked on mobile; split image/text → stacked, image first).
- **Visual details**: background, colours (hex), type scale and weights,
  spacing rhythm, radii, shadows, borders, image aspect ratios, alignment.
- **Interaction implied**: carousel arrows, tabs, accordion chevrons, hover
  states. Build what is visible; mention what you guessed.
- **Variants**: alternatives the design suggests (dark band, image on the
  other side, 2 vs 3 columns).

**When a URL is available**, open it in the browser tools available to you,
find the section, and screenshot just that section as the reference image
(save it to the workspace as `reference-<width>.png`). Then read real values
with JavaScript — `getComputedStyle` for font family/size/weight, colours,
gaps, padding, max-width — at desktop and mobile widths. Measured values beat
guesses from a compressed PNG. Use the page's copy for the sample content, but
don't copy its images or code (see content-model.md, Images).

**Screenshot only**: estimate from pixels. If you know the screenshot's
display width, scale measurements to CSS pixels. Round to the site's existing
scale where it's close.

### 2. Read the repo before designing

- `ls blocks/` and skim one or two blocks to match the house style.
- Read `styles/styles.css` for the custom properties and breakpoints actually
  in use; reuse them rather than hard-coding values.
- Read `decorateButtons` in `scripts/scripts.js` to know how CTAs become buttons.

**Reuse check — always ask.** If the section resembles a block that already
exists in the repo (cards, columns, hero, or a custom one), stop and ask the
user before building, e.g. *"This looks like `cards` with a horizontal layout.
Build it as a `cards (horizontal)` variant, or as a new `promo-grid` block?"*
Give your recommendation and the trade-off in one line. A variant means
editing that block's CSS (and maybe JS) without breaking existing uses.

Pick a name that describes the content, not the look (`stats-band`, not
`blue-row`): lowercase, hyphenated, not colliding with an existing folder.

### 3. Design the content model

Decide what the author's table looks like first, then write code to fit it.
Read `references/content-model.md` for the README format and sample-page
rules, and section 2 of `references/block-patterns.md` for choosing a shape.
The short version: one row per repeated item; text for an item in one rich-
text cell; separate cells only for structurally different things (image,
icon, stat); visual alternatives as variants in the block name.

### 4. Write the block

Read `references/block-patterns.md` and follow it. Key points: decorate
defensively (find content by element type, tolerate missing/extra cells),
semantic output (lists for repeated items, real headings, `alt` text),
`createOptimizedPicture` for images, mobile-first CSS scoped to `.<name>`,
breakpoints at 600/900/1200px with `@media (width >= …)`, site custom
properties first, block-level custom properties for any new values. No
libraries, no build step, never edit `scripts/aem.js`.

### 5. Write the sample page and README

`drafts/<name>.plain.html` with the screenshot's real copy, each variant in its
own section, and one deliberately messy instance (missing image, long title)
to prove the defensive decoration. Placeholder images in `drafts/media/` at
the design's aspect ratios. Then the README per `references/content-model.md`.

### 6. Lint

From the repo root: if `node_modules` is missing, run `npm ci` (or
`npm install`). Then `npm run lint`. Fix everything it reports in your files;
don't touch unrelated files.

### 7. Render and compare

```bash
python <skill-dir>/scripts/preview_block.py --repo <repo> \
  --page drafts/<name>.plain.html --block <name> --out <workdir>/preview
```

It serves the repo the way `aem up --html-folder drafts` would (no AEM CLI or
network needed), renders at 375, 768 and 1280px, and writes
`<name>-<width>.png` plus `report.json` (decorated?, console errors, failed
requests, horizontal overflow per width).

Then put the reference next to the render at the matching width and look at it:

```bash
python <skill-dir>/scripts/side_by_side.py reference.png <workdir>/preview/<name>-1280.png <workdir>/compare-1280.png
```

Read the comparison image and fix, in this order: anything broken (not
decorated, console errors, overflow > 0), structure and layout, spacing and
alignment, typography, colour. Two or three rounds is usually enough — aim
for "a designer would recognise it", not pixel-perfect; fonts and photos will
differ. Also look at the 375px render on its own: is it a sensible mobile
layout, not a squashed desktop?

If the user runs `aem up` themselves, the same page is at
`http://localhost:3000/drafts/<name>` with `aem up --html-folder drafts`.

### 8. Report back

Keep it short:
- the files created or changed;
- the author's table in a sentence or two, and the variants;
- what was inferred rather than seen (breakpoint behaviour, hover states,
  colours from a compressed image, fonts not in the repo);
- the final side-by-side (send the image), and any open questions for design;
- the da.live upload command from content-model.md, filled in if the user gave
  org/repo.

## Scripts

- `scripts/preview_block.py` — render a draft page through the repo and
  screenshot the block at several widths (needs Python Playwright + Chromium;
  `pip install playwright && playwright install chromium` if missing).
- `scripts/side_by_side.py` — label and stitch reference and render into one
  image (needs Pillow).
