import { createOptimizedPicture } from '../../scripts/aem.js';

export default function decorate(block) {
  const careActions = block.classList.contains('care-actions');
  /* change to ul, li */
  const ul = document.createElement('ul');
  [...block.children].forEach((row) => {
    const li = document.createElement('li');
    while (row.firstElementChild) li.append(row.firstElementChild);
    [...li.children].forEach((div) => {
      if (careActions && div.querySelector('picture img, img')) div.className = 'cards-card-icon';
      else if (div.children.length === 1 && div.querySelector('picture')) div.className = 'cards-card-image';
      else div.className = 'cards-card-body';
    });
    ul.append(li);
  });
  if (careActions) {
    ul.querySelectorAll('.cards-card-icon img').forEach((img) => {
      const image = img.closest('picture') || img;
      image.replaceWith(createOptimizedPicture(img.src, img.alt, false, [{ width: '96' }]));
    });
  } else {
    ul.querySelectorAll('picture > img').forEach((img) => img.closest('picture').replaceWith(createOptimizedPicture(img.src, img.alt, false, [{ width: '750' }])));
  }
  block.replaceChildren(ul);
}
