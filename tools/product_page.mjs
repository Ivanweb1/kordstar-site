// Карточка товара 1СК: вайб-блок Тильды, превью и страница для GitHub Pages.
// Запуск: node tools/product_page.mjs  (после python tools/catalog_page.py, если каталог пересобирался)
//
// Содержимое карточки — tilda/_doc_strop-1sk.html. Шапку, подвал, плашку cookie и поп-апы главной
// добавляет tools/tilda_block.py --doc strop-1sk, как для каталога и документов.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (name) => fs.readFileSync(path.join(root, name), 'utf8');
const write = (name, value) => fs.writeFileSync(path.join(root, name), value, 'utf8');

const python = process.platform === 'win32' ? 'python' : 'python3';
execFileSync(python, [path.join(root, 'tools', 'tilda_block.py'), '--doc', 'strop-1sk'], { cwd: root, stdio: 'inherit' });

// Ссылки сайта → адреса превью на GitHub Pages
const BASE = '/kordstar-site';
const ghLinks = (html) => html
  .replaceAll('href="/catalog#slings"', `href="${BASE}/tilda/catalog-preview.html#slings"`)
  .replaceAll('href="/catalog"', `href="${BASE}/tilda/catalog-preview.html"`)
  .replaceAll('href="/steel-ropes"', `href="${BASE}/steel-ropes.html"`)
  .replaceAll('href="/strop-1sk"', `href="${BASE}/strop-1sk.html"`)
  .replaceAll('href="/policy"', `href="${BASE}/tilda/policy-preview.html"`)
  .replaceAll('href="/soglasie"', `href="${BASE}/tilda/soglasie-preview.html"`)
  .replaceAll('href="/"', `href="${BASE}/"`);

const preview = read('tilda/strop-1sk-preview.html')
  .replace('<title>Превью вайб-блока</title>', '<title>Строп канатный 1СК — Кордстар</title>');
write('tilda/strop-1sk-preview.html', preview);
write('strop-1sk.html', ghLinks(preview));

// Страница «Стальные канаты» для GitHub Pages — из её превью (после python tools/tilda_block.py --doc steel-ropes)
write('steel-ropes.html', ghLinks(read('tilda/steel-ropes-preview.html'))
  .replace('<title>Превью вайб-блока</title>', '<title>Стальные канаты — превью Кордстар</title>'));

// В превью каталога ссылки на отдельные страницы тоже ведут на GitHub Pages
const catalog = 'tilda/catalog-preview.html';
write(catalog, read(catalog)
  .replaceAll('href="/steel-ropes"', `href="${BASE}/steel-ropes.html"`)
  .replaceAll('href="/strop-1sk"', `href="${BASE}/strop-1sk.html"`));

console.log('Готово: tilda/strop-1sk.html, tilda/strop-1sk-preview.html, strop-1sk.html');
