// Build the 1СК product block and its standalone GitHub Pages preview.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (name) => fs.readFileSync(path.join(root, name), 'utf8');
const write = (name, value) => fs.writeFileSync(path.join(root, name), value, 'utf8');

const template = read('tilda/steel-ropes.html');
const fragment = read('tilda/_product_strop-1sk.html').trim();
const start = template.indexOf('<div id="kd-catalog"');
const end = template.indexOf('</script>', start) + '</script>'.length;
if (start < 0 || end < start) throw new Error('Catalog template markers missing');

const block = (template.slice(0, start) + fragment + template.slice(end))
  .replaceAll('vb-krd-steel-ropes', 'vb-krd-strop-1sk')
  .replaceAll('Каталог стальных канатов Кордстар', 'Карточка товара Кордстар: Строп 1СК');
write('tilda/strop-1sk.html', block);

const preview = `<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Строп канатный 1СК — Кордстар</title><style>body{margin:0;--t-headline-font:"Montserrat",Arial,sans-serif;--t-text-font:"Montserrat",Arial,sans-serif}*{box-sizing:content-box}</style></head><body class="t-body"><div id="allrecords" class="t-records"><div id="rec999" class="r t-rec" data-record-type="1370">\n${block}\n</div></div></body></html>`;
write('tilda/strop-1sk-preview.html', preview);

const pages = preview
  .replaceAll('href="/catalog#slings"', 'href="/kordstar-site/tilda/catalog-preview.html#slings"')
  .replaceAll('href="/catalog"', 'href="/kordstar-site/tilda/catalog-preview.html"')
  .replaceAll('href="/policy"', 'href="/kordstar-site/tilda/policy-preview.html"')
  .replaceAll('href="/soglasie"', 'href="/kordstar-site/tilda/soglasie-preview.html"')
  .replaceAll('href="/"', 'href="/kordstar-site/"');
write('strop-1sk.html', pages);

// Keep the existing catalog's sling family card connected to the detail page.
for (const file of ['tilda/_doc_catalog.html', 'tilda/catalog.html', 'tilda/catalog-preview.html']) {
  let html = read(file);
  const marker = '<h3 class="kc-card__title">Канатные ветвевые стропы</h3>';
  const href = file.endsWith('catalog-preview.html') ? '/kordstar-site/strop-1sk.html' : '/strop-1sk';
  const link = `<a class="kc-card__detail" href="${href}" style="display:inline-block;margin:0 4px 8px;color:#204043;font-size:13px;font-weight:700;text-decoration:underline;text-underline-offset:3px">Строп 1СК →</a>`;
  if (!html.includes(marker)) throw new Error(`Sling card missing: ${file}`);
  html = html.replace(new RegExp('<a class="kc-card__detail"[^>]*>Строп 1СК →<\\/a>', 'g'), '');
  html = html.replace(marker, marker + link);
  write(file, html);
}

console.log('Built tilda/strop-1sk.html, preview, and strop-1sk.html');
