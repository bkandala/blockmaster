# Cards

The Cards block displays repeated items in a responsive grid. Use the `care-actions` variant for a row of icon-led actions with a heading, description, and pill-shaped call to action.

## Authoring (da.live)

For `Cards (care-actions)`, use one row per action and two cells per row:

| Cards (care-actions) | |
|---|---|
| *icon image* | **Heading 3:** Call 24/7 for advice<br>If you need help choosing the care that’s right for you, give us a call.<br>**[Call us](/contact-us/)** |
| *icon image* | **Heading 3:** Message your care team<br>Prefer to write? Message your care team anytime with medical questions.<br>**[Compose a message](/secure/messages)** |

- **Icon cell:** one small square icon image, ideally at least 96 × 96 pixels, with meaningful alt text. Use only one image-containing cell per row; missing icons are allowed.
- **Text cell:** keep the heading, description, and CTA together. Use a bold link on its own line for the blue primary button.
- Empty or extra cells are tolerated. Image-containing cells are styled as icons; keep all heading, description, and CTA content together in the text cell.

## Variants

| Block name | Result |
|---|---|
| `Cards` | Existing responsive image cards |
| `Cards (care-actions)` | Icon, heading, description, and pill CTA per item |

## Layout

- **Phone (< 600px):** one stacked action per row; buttons fill the available width.
- **Tablet (600–899px):** two columns.
- **Desktop (≥ 900px):** three columns; buttons use their natural width.

## Sample

The sample page is [drafts/cards.plain.html](../../drafts/cards.plain.html), with placeholder icons in `drafts/media/`. Preview locally with `npx -y @adobe/aem-cli up --html-folder drafts` at `http://localhost:3000/drafts/cards`.

Upload the sample to da.live at `https://da.live/edit#/bkandala/blockmaster/drafts/cards`. Upload the `drafts/media/cards-*` images first, then upload the page HTML with those image paths rewritten to `https://content.da.live/bkandala/blockmaster/drafts/media/`.
