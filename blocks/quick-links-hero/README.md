# Quick Links Hero

A photo with a white card overlapping it. The card holds a heading, optional text, and a set of
pill-shaped quick links ("chips"). Built from the "Today's suggestions" section of a member
front-door page.

## Authoring (da.live)

One table, one row, two cells:

| Quick Links Hero | |
|---|---|
| *image* | **Heading 3:** Today's suggestions:<br>• [Care in Nevada](/learn/about-nevada)<br>• [Mental health services](/health-wellness/mental-health/services)<br>• [Get a flu shot](/health-wellness/flu) |

- **Image cell:** one image, ideally landscape 3:2, at least 1600px wide. Always fill in the alt text.
  The first image anywhere in the block is used; others are ignored.
- **Content cell:**
  - **Heading 3** (or 4-6) gives the small navy label. **Heading 2** gives a big title, for promo
    use like "Find a health plan that's right for you".
  - **Bulleted list of links** becomes the chips. Each bullet should be just one link.
    Links typed as separate paragraphs (one link per paragraph) also become chips.
  - **Bold link** on its own line stays a primary button, **italic link** a secondary button,
    for a CTA under body text.
  - Plain paragraphs show as body text.
- Cells can be in either order, or the image and text can share one cell; empty cells are ignored.
- No image: the card shows on its own, full width. No text: the image shows on its own.

## Variants

| Block name | Result |
|---|---|
| `Quick Links Hero` | Image on the left, card overlapping on the right (desktop) |
| `Quick Links Hero (image-right)` | Mirrored: image on the right, card on the left |

Put the block in a section with **Section Metadata → Style: light** to get the grey band behind it.

## Layout

- **Phone (< 600px):** image full-bleed at 3:2, card below it overlapping the image bottom by 80px.
- **Tablet (600-899px):** image keeps the page gutter with rounded corners; card inset 24px.
- **Desktop (≥ 900px):** image spans 10 of 12 columns; card spans 5 columns over the far edge,
  vertically centred.

## Sample

`drafts/quick-links-hero.plain.html` (images in `drafts/media/`). Locally:
`npx -y @adobe/aem-cli up --html-folder drafts`, then open
`http://localhost:3000/drafts/quick-links-hero`.
