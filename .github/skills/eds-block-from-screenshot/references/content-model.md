# Content model, README and sample page

A block nobody can author is useless. These files are what authors use.

## The block README (`blocks/<name>/README.md`)

`*.md` is in the boilerplate's `.hlxignore`, so the README is not served. Check
`.hlxignore` in the repo; add `*.md` if it's missing, since all committed files are
otherwise public. Keep it short and written for authors, not developers:

```markdown
# <Block Title>

One or two sentences: what it looks like and when to use it.

## Authoring (da.live)

| <Block Title> | |
|---|---|
| *image* | **Heading 2:** Title<br>Body text<br>**[Bold link](/path)** |

- **Image cell:** what goes there, preferred aspect ratio and minimum width, alt text.
- **Text cell:** which heading level does what, how links/buttons behave
  (bold link = primary button, italic = secondary, bulleted links = …).
- What happens when a cell is empty or missing.

## Variants

| Block name | Result |
|---|---|
| `<Block Title>` | default |
| `<Block Title> (dark)` | … |

## Layout

Phone / tablet / desktop behaviour in one line each.

## Sample

Where the sample page lives and how to preview it.
```

## The sample page (`drafts/<name>.plain.html`)

`.plain.html` is the HTML the backend produces for a page body: sections as top-level
`<div>`s, blocks as `<div class="<name> <variant>">` with row/cell divs. No `<html>`,
`<head>` or `<main>`.

```html
<div>
  <h1><Block title> sample</h1>
  <p>What this page shows.</p>
</div>
<div>
  <div class="my-block">
    <div>
      <div><picture><img src="./media/my-block-1.jpg" alt="…" width="1500" height="1000"></picture></div>
      <div><h2>Real copy from the screenshot</h2><p>…</p><p><strong><a href="/x">CTA</a></strong></p></div>
    </div>
  </div>
  <div class="section-metadata">
    <div><div>Style</div><div>light</div></div>
  </div>
</div>
<div>
  <div class="my-block dark">…</div>
</div>
<div>
  <h2>Messy instance</h2>
  <div class="my-block">
    <div><div><h2>A very long title that will certainly wrap onto several lines on a phone</h2></div><div></div></div>
  </div>
</div>
```

Rules:

- **Use the screenshot's real copy** so the comparison is honest.
- **One section per variant**, plus **one deliberately messy instance**: missing image,
  a very long title or link, an extra empty cell, links typed as paragraphs instead of
  a list. It proves the defensive decoration.
- Section styles go in a `section-metadata` div as the **last** child of the section.
- Image `src` values are **relative** (`./media/…`) so the same file works locally and
  after upload.
- Sample link `href`s should be site-relative paths, not the reference site's domain.

### Images

- **Don't copy the reference site's images or code.** Use placeholders in
  `drafts/media/` at the design's aspect ratios (e.g. a 1500×1000 JPEG for 3:2) with a
  visible label, so nobody mistakes them for final art. Real imagery is the author's
  job, unless the user supplies files they have rights to.
- Name images after the block: `my-block-<what>.jpg`.

### Preview

- Locally with the AEM CLI: `npx -y @adobe/aem-cli up --html-folder drafts`, then
  `http://localhost:3000/drafts/<name>`.
- Without the CLI or network: `scripts/preview_block.py`.

## Putting the sample in da.live

da.live stores a page as HTML: `<body><header></header><main>…sections…</main><footer></footer></body>`,
with blocks as `<div class="name variant">`. The editor shows them as tables.

Upload with the DA admin API (an Adobe IMS token for someone with write access to the
org in `$DA_TOKEN`; in the da.live tab, `adobeIMS.getAccessToken().token` in the browser
console returns it). Upload the images first, then the page with its image `src`s
pointing at their da.live copies:

```bash
ORG=<org>; REPO=<repo>; NAME=<block-name>
for f in drafts/media/$NAME-*; do
  curl -sS -X PUT "https://admin.da.live/source/$ORG/$REPO/$f" \
    -H "Authorization: Bearer $DA_TOKEN" -F "data=@$f"
done
{ echo '<body><header></header><main>'
  sed "s#\./media/#https://content.da.live/$ORG/$REPO/drafts/media/#g" drafts/$NAME.plain.html
  echo '</main><footer></footer></body>'; } > /tmp/$NAME.html
curl -sS -X PUT "https://admin.da.live/source/$ORG/$REPO/drafts/$NAME.html" \
  -H "Authorization: Bearer $DA_TOKEN" -F "data=@/tmp/$NAME.html;type=text/html"
```

Check first that the path is free (`GET https://admin.da.live/list/$ORG/$REPO/drafts`);
`PUT` overwrites without asking. Then open
`https://da.live/edit#/$ORG/$REPO/drafts/$NAME`, click **Preview**, and the page is at
`https://main--$REPO--$ORG.aem.page/drafts/$NAME` (or `<branch>--…` for a branch).

If the sample now lives in da.live, remove `drafts/<name>.plain.html` and its media from
the repo: committed files are served.
