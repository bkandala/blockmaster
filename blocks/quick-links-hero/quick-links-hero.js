import { createOptimizedPicture } from '../../scripts/aem.js';

/**
 * True when an element holds a single link and no other text,
 * e.g. <li><a>Get a flu shot</a></li> or <p><a>Shop plans</a></p>.
 * Paragraphs already turned into buttons by decorateButtons are skipped.
 * @param {Element} el
 * @returns {HTMLAnchorElement|null}
 */
function soleLink(el) {
  if (el.classList.contains('button-wrapper')) return null;
  const links = el.querySelectorAll('a[href]');
  if (links.length !== 1) return null;
  const [a] = links;
  return a.textContent.trim() && el.textContent.trim() === a.textContent.trim() ? a : null;
}

function chip(a) {
  const li = document.createElement('li');
  a.className = 'quick-links-hero-link';
  a.title = a.title || a.textContent.trim();
  li.append(a);
  return li;
}

/**
 * Turns authored link lists, and runs of link-only paragraphs, into a chip list.
 * Bold/italic links stay buttons (decorateButtons), so authors can still add a CTA.
 * @param {Element} card
 */
function buildLinks(card) {
  let run = null;
  [...card.children].forEach((el) => {
    if ((el.tagName === 'UL' || el.tagName === 'OL') && [...el.children].length
      && [...el.children].every((li) => soleLink(li))) {
      const ul = document.createElement('ul');
      ul.className = 'quick-links-hero-links';
      [...el.children].forEach((li) => ul.append(chip(soleLink(li))));
      el.replaceWith(ul);
      run = null;
      return;
    }
    const a = el.tagName === 'P' ? soleLink(el) : null;
    if (a) {
      if (!run) {
        run = document.createElement('ul');
        run.className = 'quick-links-hero-links';
        el.before(run);
      }
      run.append(chip(a));
      el.remove();
      return;
    }
    run = null;
  });
}

export default function decorate(block) {
  const cells = [...block.children].flatMap((row) => [...row.children]);

  // the first picture anywhere in the block is the media; everything else is card content
  const img = block.querySelector('picture img, img');
  const media = document.createElement('div');
  media.className = 'quick-links-hero-media';
  if (img) {
    const picture = createOptimizedPicture(img.src, img.alt || '', true, [
      { media: '(width >= 900px)', width: '1600' },
      { width: '750' },
    ]);
    media.append(picture);
    (img.closest('picture') || img).remove();
  }

  const card = document.createElement('div');
  card.className = 'quick-links-hero-card';
  cells.forEach((cell) => {
    [...cell.children].forEach((el) => {
      // drop wrappers left empty after the picture moved out
      if (!el.textContent.trim() && !el.querySelector('img, picture, a')) return;
      card.append(el);
    });
    // text typed straight into a cell, without a paragraph around it
    const loose = cell.textContent.trim();
    if (loose && !cell.children.length) {
      const p = document.createElement('p');
      p.textContent = loose;
      card.append(p);
    }
  });

  buildLinks(card);

  const children = [];
  if (img) children.push(media);
  else block.classList.add('no-media');
  if (card.children.length) children.push(card);
  else block.classList.add('no-card');
  block.replaceChildren(...children);
}
