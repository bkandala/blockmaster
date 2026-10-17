# Block patterns

How to write an Edge Delivery block that survives real authors. The repo's own
`AGENTS.md`/`CLAUDE.md` and existing blocks win over anything here.

## 1. What the block receives

The page's HTML arrives from the backend already parsed into rows and cells:

```html
<div class="my-block variant-a">      <!-- block name + variants, lowercased, hyphenated -->
  <div>                                <!-- row -->
    <div><picture>…</picture></div>    <!-- cell -->
    <div><h2>…</h2><p>…</p></div>      <!-- cell -->
  </div>
</div>
```

Before `decorate(block)` runs, `scripts/scripts.js` has already:

- run `decorateButtons`: a paragraph holding only a **bold** link becomes
  `p.button-wrapper > a.button.primary`, an *italic* link `a.button.secondary`,
  bold + italic `a.button.accent`. Plain links are left alone. Read the repo's
  version: forks change these rules.
- run `decorateIcons`: `:name:` became `<span class="icon icon-name">`.
- run `buildAutoBlocks`, which may have rewritten content (e.g. a hero built from
  the first image and heading).
- wrapped sections; Section Metadata is applied by the backend as section classes
  (`Style`) and `data-*` attributes. In current boilerplates `aem.js` does not handle
  it, so a local server must do it (`scripts/preview_block.py` does).

The block's CSS and JS load lazily, per block, the first time the block is on the page.

## 2. Choosing a content shape

Design the author's table before writing code. The table is the API.

| The section has… | Table shape |
|---|---|
| N repeated items (cards, stats, logos, steps) | **one row per item**; cells inside a row = the item's parts |
| One unit: media + text (hero, promo, split) | **one row, two cells**: image \| text. Accept either order. |
| A heading/intro above repeated items | put the intro in **default content above the block**, not in the block |
| Key/value settings (autoplay, interval) | rows of `key \| value`, read with `readBlockConfig` |
| Tabs / accordion | one row per panel: label cell \| content cell |

Rules of thumb:

- **Text for one item goes in one rich-text cell.** Heading, body and CTA live together;
  find them by element type, not by position. Authors write this naturally.
- **Separate cells only for structurally different things**: image, icon, a stat number,
  a link that wraps the whole card.
- **Visual alternatives are variants** in the block name (`Cards (horizontal, dark)` →
  `.cards.horizontal.dark`), not extra cells or config rows. Name variants by intent
  (`image-right`, `dark`, `compact`), never by pixel values.
- **Lists stay lists.** A bulleted list of links is the natural authoring form for
  chips, link groups and nav-like rows.
- **Plain heading + text areas are default content**, not a block.
- Don't invent a field the screenshot doesn't need. Every cell is a thing an author
  can get wrong.

## 3. Writing `decorate`

```js
import { createOptimizedPicture } from '../../scripts/aem.js';

export default function decorate(block) {
  const ul = document.createElement('ul');
  [...block.children].forEach((row) => {
    const li = document.createElement('li');
    li.className = 'my-block-item';
    const picture = row.querySelector('picture');
    if (picture) {
      const img = picture.querySelector('img');
      const media = document.createElement('div');
      media.className = 'my-block-media';
      media.append(createOptimizedPicture(img.src, img.alt, false, [{ width: '750' }]));
      li.append(media);
      picture.remove();
    }
    const body = document.createElement('div');
    body.className = 'my-block-body';
    row.querySelectorAll(':scope > div > *').forEach((el) => {
      if (el.textContent.trim() || el.querySelector('a, img')) body.append(el);
    });
    if (body.children.length) li.append(body);
    if (li.children.length) ul.append(li);
  });
  block.replaceChildren(ul);
}
```

Decorate defensively:

- **Find content by element type**, never `children[1].children[0]`. Authors omit,
  reorder and add cells.
- **Tolerate missing pieces**: no image → add a `no-media` class and lay out text-only;
  no text → image only. Never throw. An exception leaves the block undecorated.
- **Ignore empty cells and empty paragraphs** (authors leave them behind).
- **Wrap loose text** typed straight into a cell in a `<p>`.
- **Keep authored headings.** Don't change their level; style them by context.
- **Use `textContent`/DOM APIs, not `innerHTML`** with content. The boilerplate's CSP
  sets `require-trusted-types-for 'script'`, so `innerHTML` assignments throw.
- **Prefix every class** with the block name (`my-block-item`) so styles never leak.
- **No libraries, no build step, no network calls** for content that's already in the
  table. The only allowed cross-block import is `fragment/fragment.js`; shared helpers
  come from `/scripts/`. Never edit `scripts/aem.js`.
- **Interaction** (carousel, tabs, accordion): real `<button>`s with `aria-controls`,
  `aria-expanded` / `aria-selected`, keyboard support, and `prefers-reduced-motion`
  respected. Native `<details>` is often enough for an accordion.

## 4. Semantic output

- Repeated items → `ul > li` (or `ol` for ordered steps).
- Real headings, in the author's order. Don't promote a label to a heading in JS.
- Every image keeps its alt text; decorative images get `alt=""`.
- Links stay `<a href>`; buttons that don't navigate are `<button type="button">`.
- Whole-card links: keep one real link and stretch it with CSS
  (`.my-block-item a::after { content: ''; position: absolute; inset: 0; }`)
  instead of wrapping block-level content in `<a>`.

## 5. Images

- Always rebuild with `createOptimizedPicture(src, alt, eager, breakpoints)`. It emits
  WebP sources and width-limited URLs from the media bus.
- `eager = true` only for an above-the-fold hero (it's the LCP image); everything
  else stays lazy.
- Breakpoints: request roughly the largest rendered width, e.g.
  `[{ media: '(width >= 900px)', width: '1600' }, { width: '750' }]` for a wide hero,
  `[{ width: '750' }]` for cards.
- Fix the frame in CSS (`aspect-ratio` + `object-fit: cover`) so author images of any
  shape don't break the layout.

## 6. CSS

- **Mobile-first**, scoped to `.my-block` (never style `-wrapper` / `-container`
  except to undo section padding for full-bleed, and say so in a comment).
- **Breakpoints** `@media (width >= 600px)`, `(width >= 900px)`, `(width >= 1200px)`.
  Match the repo if it uses others.
- **Site custom properties first**: `--text-color`, `--link-color`, `--background-color`,
  `--light-color`, `--body-font-family`, `--heading-font-family`, the
  `--heading-font-size-*` / `--body-font-size-*` scales. Read `styles/styles.css` to see
  what exists.
- **New values become block-level custom properties** at the top of the block rule
  (`--my-block-accent: #003b71;`) so a theme can override them in one place.
- Section gutters come from `main > .section > div` (often `0 24px`, `0 32px` from
  900px). Full-bleed media on phones cancels that gutter with a negative margin.
- Use `display: grid` / `flex` with `gap`; avoid fixed heights. Long titles and long
  link text must wrap (`overflow-wrap: break-word`, `min-width: 0` on grid children).
- Hover and focus together; visible `:focus-visible` outlines.
- No horizontal page scroll at any width (`preview_block.py` reports overflow).
- Lint with the repo's `stylelint` config (`npm run lint`).

## 7. Variants

Variants are classes on the block. Implement them in the same CSS/JS:

```css
.my-block.image-right .my-block-media { order: 2; }
```

When adding a variant to an **existing** block, keep the default rendering
byte-for-byte identical; existing pages must not change. Test an existing page too.

## 8. Before you call it done

- [ ] Decorates the sample page with zero console errors at 375 / 768 / 1280px
- [ ] Messy instance (missing image, long title, extra/empty cells) still renders sensibly
- [ ] No horizontal overflow
- [ ] `npm run lint` clean for the new files
- [ ] README written for authors (see `content-model.md`)
- [ ] Side-by-side with the reference looks like the same design
