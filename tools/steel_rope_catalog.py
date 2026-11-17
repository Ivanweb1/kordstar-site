"""Build the steel-rope catalogue from data/steel_ropes.json.

The JSON is a faithful export of the supplied workbook. Identical duplicate
rows are collapsed; empty values are never inferred.
"""
import html
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'tilda' / '_doc_steel-ropes.html'
ROWS = json.loads((ROOT / 'data' / 'steel_ropes.json').read_text(encoding='utf-8'))

def esc(value):
    return html.escape(value or '', quote=True)

def numeric(value):
    return float(value.replace(',', '.'))

def select(field, label, values):
    options = ''.join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in values)
    return (f'<label class="kc-filter"><span>{label}</span><select data-kc-filter="{field}">'
            f'<option value="">Все</option>{options}</select></label>')

diameters = sorted({r['A'] for r in ROWS}, key=numeric)
constructions = sorted({r['C'] for r in ROWS})
coatings = sorted({r['D'] for r in ROWS})
lays = sorted({r['E'] for r in ROWS})
applications = sorted({v.strip() for r in ROWS for v in r['F'].split(',') if v.strip()})
filters = ('<div class="kc-filters" aria-label="Фильтры канатов">'
           + select('diameter', 'Диаметр, мм', diameters)
           + select('construction', 'Конструкция', constructions)
           + select('coating', 'Покрытие', coatings)
           + select('lay', 'Свивка', lays)
           + select('application', 'Применение', applications)
           + '</div>')

specs = [('H', 'Количество прядей'), ('J', 'Сердечник'), ('K', 'Направление свивки'),
         ('L', 'Тип свивки'), ('M', 'Обозначение свивки'), ('N', 'Покрытие проволоки'),
         ('O', 'Некрутящийся канат'), ('P', 'Временное сопротивление разрыву')]

def card(row, rank):
    title = f"Канат {row['B']} · {row['A']} мм"
    traits = ' · '.join((row['C'], row['D'], row['E']))
    details = ''.join(f'<div><dt>{esc(label)}</dt><dd>{esc(row[key])}</dd></div>'
                      for key, label in specs if row[key])
    benefits = ''.join(f'<li>{esc(row[key])}</li>' for key in 'RST' if row[key])
    return (
        f'<article class="kc-card kc-rope-card" data-kc-cat="ropes" data-kc-name="{esc(title.lower())}" '
        f'data-kc-rank="{rank}" data-kc-diameter="{esc(row["A"])}" '
        f'data-kc-construction="{esc(row["C"])}" data-kc-coating="{esc(row["D"])}" '
        f'data-kc-lay="{esc(row["E"])}" data-kc-application="{esc(row["F"])}">'
        f'<h3 class="kc-card__title">{esc(title)}</h3>'
        f'<p class="kc-rope-traits">{esc(traits)}</p>'
        f'<p class="kc-card__text">{esc(row["Q"])}</p>'
        f'<details class="kc-rope-detail"><summary>Характеристики и преимущества</summary>'
        f'<dl>{details}</dl><p><b>Применение:</b> {esc(row["F"])}</p>'
        f'<ul>{benefits}</ul><p><b>Сертификаты:</b> {esc(row["U"].strip())}</p></details>'
        f'<p class="kc-card__price">Цена по запросу</p>'
        f'<button class="kc-card__btn" type="button" data-krd-popup="order" '
        f'data-kc-product="{esc(title)}">Предзаказ</button></article>')

group = ('<section class="kc-group" data-kc-group="ropes">'
         f'<div class="kc-group__head"><div><h2 class="kc-group__title">Канаты в каталоге '
         f'<span class="kc-group__count" data-kc-count>{len(ROWS)}</span></h2>'
         f'<p class="kc-group__lead">Диаметр {diameters[0]}–{diameters[-1]} мм. '
         'Выберите параметры или найдите канат по обозначению.</p></div></div>'
         '<div class="kc-grid">' + ''.join(card(r, i) for i, r in enumerate(ROWS)) + '</div></section>')

style = '''
.vb-krd .kc-filters{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin:-16px 0 30px}
.vb-krd .kc-filter{min-width:0;font-size:12px;font-weight:600;color:var(--kc-muted)}
.vb-krd .kc-filter span{display:block;margin:0 0 6px}
.vb-krd .kc-filter select{width:100%;height:40px;padding:0 10px;border:1px solid var(--kc-line);border-radius:12px;background:#fff;color:var(--kc-ink);font:inherit;font-weight:400}
.vb-krd .vb-krd-cat .kc-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.vb-krd .kc-rope-card{padding:22px;gap:8px}
.vb-krd .kc-rope-card .kc-card__title{margin:0;font-size:17px}
.vb-krd .kc-rope-traits{margin:0;color:var(--kc-accent);font-size:12px;line-height:1.4}
.vb-krd .kc-rope-card .kc-card__text{margin:4px 0;font-size:13px}
.vb-krd .kc-rope-detail{font-size:12px;line-height:1.5;color:var(--kc-ink)}
.vb-krd .kc-rope-detail summary{cursor:pointer;color:var(--kc-accent);font-weight:600}
.vb-krd .kc-rope-detail dl{margin:12px 0;display:grid;gap:5px}
.vb-krd .kc-rope-detail dl div{display:grid;grid-template-columns:1fr 1fr;gap:8px;border-bottom:1px solid var(--kc-line);padding:3px 0}
.vb-krd .kc-rope-detail dt{color:var(--kc-muted)}
.vb-krd .kc-rope-detail dd{margin:0}
.vb-krd .kc-rope-detail ul{padding-left:18px}
.vb-krd .kc-rope-card .kc-card__price{margin:auto 0 0}
@media(max-width:959px){.vb-krd .kc-filters{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:639px){.vb-krd .kc-filters{grid-template-columns:repeat(2,minmax(0,1fr))}.vb-krd .vb-krd-cat .kc-grid{grid-template-columns:1fr}}
'''

js = '''
  var filters = [].slice.call(root.querySelectorAll('[data-kc-filter]'));
  function matchesFilters(card) {
    return filters.every(function (filter) {
      var value = filter.value;
      if (!value) return true;
      var field = filter.getAttribute('data-kc-filter');
      var stored = card.getAttribute('data-kc-' + field) || '';
      return field === 'application' ? stored.split(',').map(function (v) { return v.trim(); }).indexOf(value) !== -1 : stored === value;
    });
  }
  filters.forEach(function (filter) { filter.addEventListener('change', apply); });
'''

text = PAGE.read_text(encoding='utf-8')
text = text.replace('Диаметр от 3 до 100 мм.', f'Диаметр {diameters[0]}–{diameters[-1]} мм.')
if '<!-- rope-filters -->' not in text:
    anchor = '<section class="kc-group" data-kc-group="ropes">'
    text = text.replace(anchor, '<!-- rope-filters -->' + filters + '<!-- /rope-filters -->\n' + anchor, 1)
else:
    text = re.sub(r'<!-- rope-filters -->.*?<!-- /rope-filters -->',
                  '<!-- rope-filters -->' + filters + '<!-- /rope-filters -->', text, count=1, flags=re.S)
text, replaced = re.subn(r'<section class="kc-group" data-kc-group="ropes">.*?</section>',
                         lambda _: group, text, count=1, flags=re.S)
if replaced != 1:
    raise RuntimeError('Steel rope product section not found')
text = re.sub(r'(?s)<!-- rope-style -->.*?<!-- /rope-style -->', '', text)
text = text.replace('</style>', '<!-- rope-style -->' + style + '<!-- /rope-style -->\n</style>', 1)
if 'var filters = [].slice.call' not in text:
    text = text.replace('  function apply() {', js + '\n  function apply() {', 1)
text = text.replace("c.querySelector('.kc-card__text').textContent.toLowerCase().indexOf(q) !== -1;",
                    "c.textContent.toLowerCase().indexOf(q) !== -1;", 1)
text = text.replace('c.hidden = !hit;', 'c.hidden = !hit || !matchesFilters(c);', 1)
text = text.replace('if (hit) n++;', 'if (!c.hidden) n++;', 1)
if "var count = root.querySelector('[data-kc-count]')" not in text:
    text = text.replace('    empty.classList.toggle', "    var count = root.querySelector('[data-kc-count]');\n    if (count) count.textContent = shown;\n    empty.classList.toggle", 1)
text = text.replace("if (e.target.closest('[data-kc-reset]')) { search.value = ''; show('all', true); return; }",
                    "if (e.target.closest('[data-kc-reset]')) { search.value = ''; filters.forEach(function (f) { f.value = ''; }); show('all', true); return; }", 1)
PAGE.write_text(text, encoding='utf-8', newline='\n')
subprocess.run([sys.executable, str(ROOT / 'tools' / 'tilda_block.py'), '--doc', 'steel-ropes'], check=True)
preview = (ROOT / 'tilda' / 'steel-ropes-preview.html').read_text(encoding='utf-8')
base = '/kordstar-site'
for old, new in (
    ('href="/catalog"', f'href="{base}/tilda/catalog-preview.html"'),
    ('href="/policy"', f'href="{base}/tilda/policy-preview.html"'),
    ('href="/soglasie"', f'href="{base}/tilda/soglasie-preview.html"'),
    ('href="/"', f'href="{base}/"'),
):
    preview = preview.replace(old, new)
preview = preview.replace('<title>Превью вайб-блока</title>',
                          '<title>Стальные канаты — Кордстар</title>')
(ROOT / 'steel-ropes.html').write_text(preview, encoding='utf-8', newline='\n')
print(f'Built {len(ROWS)} steel rope positions')
