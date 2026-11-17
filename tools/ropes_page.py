# Страница «Стальные канаты» из таблицы data/steel-ropes.xlsx по прототипу design/kordstar-prototypes.fig
# (раздел «Каталог / Стальные канаты»), в стиле сайта.
# Запуск: python tools/ropes_page.py  → обновляет tilda/_doc_steel-ropes.html, затем собирает
# tilda/steel-ropes.html, превью и steel-ropes.html для GitHub Pages (через tilda_block.py и product_page.mjs).
#
# Одна строка таблицы — один диаметр. На сайте одна карточка на марку (полный код, например
# 35WxK7-zZ-Galv-2160): фото, название, пояснение, цена, «Предзаказ» — как в прототипе. По клику на карточку
# открывается окно с описанием, преимуществами, характеристиками и выбором диаметра.
# Фильтры как в прототипе: диаметр «От — До», конструкция, тип покрытия, направление свивки, применение.
# Применение задаётся у каждого диаметра отдельно, поэтому фильтр проверяет строки, а не марку.
# Под каталогом — раскрывающиеся блоки «Как выбрать?» и «Где применяется?» (тексты из прототипа).
import html, json, os, re, subprocess, sys
from collections import OrderedDict

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, 'data', 'steel-ropes.xlsx')
DOC = os.path.join(ROOT, 'tilda', '_doc_steel-ropes.html')
ICON = 'img/Frame_2136139848-32303965.webp'
FIXES = []  # что поправили в данных — печатаем в конце

# порядок и подписи фильтров — из прототипа
CONSTR_ORDER = ['35WxK7', '34WxK7', '24WxK7', '19xK7', '18xK7', '16xK7', '15xK7', '8xK26WS', '8xK36WS', '6x19W',
                '4xV39S', '6x36', 'ГОСТ 7668-80', 'ГОСТ 7669-80', 'ГОСТ 2688-80']
COAT_ORDER = ['Galv (оцинкованный)', 'Ung (неоцинкованный)']
LAY_ORDER = ['zZ (RHLL)', 'sS (LHLL)', 'sZ (RHRL)', 'zS (LHRL)']
APP_ORDER = ['Буровая установка', 'Башенный кран', 'Автокран', 'Гусеничный кран', 'Мостовой кран', 'Козловой кран',
             'Манипулятор', 'Трубоукладчик', 'Эвакуатор', 'Лебедка', 'Растяжка']
# названия в таблице → названия в прототипе
APP_NAME = {'Козловые краны': 'Козловой кран', 'Растяжки': 'Растяжка', 'Ратяжки': 'Растяжка'}
LAY = {'sZ': ('Правая', 'Крестовая'), 'zZ': ('Правая', 'Односторонняя'),
       'sS': ('Левая', 'Односторонняя'), 'zS': ('Левая', 'Крестовая')}
LAY_FILTER = {'sZ': 'sZ (RHRL)', 'zZ': 'zZ (RHLL)', 'sS': 'sS (LHLL)', 'zS': 'zS (LHRL)'}

HOWTO = [('Назначение', 'Определите, для чего нужен канат: подъём, буксировка, растяжка, ограждение и т.д.'),
         ('Материал', 'Стальной — для высокой нагрузки и прочности. Синтетический — легче, устойчив к влаге и коррозии.'),
         ('Диаметр', 'Количество прядей и тип свивки влияют на гибкость и износостойкость.'),
         ('Покрытие', 'Оцинковка или ПВХ-защита — для работы на улице и во влажной среде.'),
         ('Соответствие DIN', 'Убедитесь, что канат соответствует нужному DIN-стандарту (например, DIN 3055, DIN 3060 и др.).')]
WHERE = [('Строительство', 'подъём и перемещение грузов'), ('Промышленность', 'оборудование, краны, лебёдки'),
         ('Судоходство', 'швартовка, такелаж'), ('Авто и транспорт', 'буксировка, крепление грузов'),
         ('Инфраструктура', 'мосты, ограждения, тросовые системы'), ('Быт и туризм', 'палатки, страховка, хозяйственные задачи')]


def norm_x(s):
    """35W×K7 / 6х19W → 35WxK7 / 6x19W: как в прототипе и в каталоге сайта."""
    return re.sub(r'(?<=[0-9A-Za-z])[xх×](?=[0-9A-Za-z])', 'x', s)


def base_constr(s):
    """Конструкция для фильтра: без сердечника, ГОСТ — отдельным пунктом, как в прототипе."""
    s = norm_x(s)
    m = re.search(r'ГОСТ\s*[\d-]+', s)
    if m:
        return m.group(0)
    return re.sub(r'-(IWRC|PWRC\(K\)|WSC|FC).*$', '', s)


def diam(v):
    num = float(str(v).strip().replace(',', '.'))
    return num, ('%g' % num).replace('.', ',')


def load():
    ws = openpyxl.load_workbook(XLSX, data_only=True).active
    cards = OrderedDict()
    for n, r in enumerate(ws.iter_rows(min_row=3, values_only=True), 3):
        if not r[1]:
            continue
        r = [c.strip() if isinstance(c, str) else c for c in r]
        code = r[1]
        num, label = diam(r[0])
        if isinstance(r[0], (int, float)):
            FIXES.append('строка %d: диаметр %r записан числом, а не текстом «%s,0»' % (n, r[0], label))
        apps = []
        for a in str(r[5]).split(','):
            a = a.strip()
            if not a or a == 'Иное':
                continue
            if a == 'Ратяжки' or a == 'Растяжка':
                FIXES.append('строка %d: «%s» вместо «Растяжки»' % (n, a))
            a = APP_NAME.get(a, a)
            if a not in apps:
                apps.append(a)
        lay = r[12]
        dir_, kind = LAY[lay]
        if r[10] != dir_:
            FIXES.append('строка %d (%s, %s мм): направление свивки «%s», а %s — «%s»' % (n, code, label, r[10], lay, dir_))
        core = r[9]
        if 'PWRC' in code and 'PWRC' not in core:
            FIXES.append('строка %d (%s, %s мм): сердечник «%s», а в марке PWRC(K)' % (n, code, label, core))
            core = 'Стальной с пластически обжатыми прядями (PWRC(K))'
        nonrot = str(r[14]).capitalize()
        if r[14] != nonrot:
            FIXES.append('строка %d: «%s» с маленькой буквы (некрутящийся)' % (n, r[14]))
        c = cards.get(code)
        if c is None:
            galv = 'Galv' in r[3]
            c = cards[code] = dict(
                code=norm_x(code), constr=norm_x(r[8]), fconstr=base_constr(r[2]),
                coat='Оцинкованный' if galv else 'Без покрытия', fcoat=r[3],
                lay=lay, flay=LAY_FILTER[lay], dir=dir_, kind=kind, core=core,
                strands=str(r[7]), nonrot=nonrot, strength=r[15],
                coating=('Оцинкованная' if galv else 'Неоцинкованная'),
                desc=r[16], adv=[a for a in (r[17], r[18], r[19]) if a], cert=r[20] or 'По запросу', rows=[])
        if any(x['label'] == label for x in c['rows']):
            FIXES.append('строка %d: %s, %s мм — повтор строки' % (n, code, label))
            continue
        c['rows'].append(dict(num=num, label=label, apps=apps))
    for c in cards.values():
        c['rows'].sort(key=lambda x: x['num'])
    return list(cards.values())


def esc(s):
    return html.escape(str(s), quote=True)


def adv_html(a):
    m = re.match(r'([^.]+\.)\s*(.*)', a)
    return '<li><b>%s</b> %s</li>' % (esc(m.group(1)), esc(m.group(2))) if m else '<li>%s</li>' % esc(a)


ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
         'stroke-linejoin="round" aria-hidden="true"><path d="m6 15 6-6 6 6"/></svg>')


def present(order, values):
    return [o for o in order if o in values] + sorted(v for v in values if v not in order)


def build(cards):
    diams_all, apps_all = {}, set()
    for c in cards:
        for r in c['rows']:
            diams_all[r['label']] = r['num']
            apps_all.update(r['apps'])
    diams = sorted(diams_all, key=lambda k: diams_all[k])
    apps = present(APP_ORDER, apps_all)

    def opts(gid, values):
        return '<ul class="kr-f-list">%s</ul>' % ''.join(
            '<li><label class="kr-f-opt"><input type="checkbox" data-kr-f="%s" data-kr-v="%s"><i></i><span>%s</span>'
            '<em data-kr-n></em></label></li>' % (gid, esc(v), esc(v)) for v in values)

    def group(title, body):
        return ('<details class="kr-f-group" open><summary>%s%s</summary>%s</details>' % (title, ARROW, body))

    last = len(diams) - 1
    side = (
        '<p class="kr-side__title">Фильтры</p>'
        '<div class="kr-f-group kr-f-range"><p class="kr-f-head">Диаметр каната, мм</p>'
        '<div class="kr-range__fields"><label><span>От</span><input type="text" inputmode="decimal" data-kr-from value="%s" aria-label="Диаметр от, мм"></label>'
        '<label><span>До</span><input type="text" inputmode="decimal" data-kr-to value="%s" aria-label="Диаметр до, мм"></label></div>'
        '<div class="kr-range"><i class="kr-range__fill" data-kr-fill></i>'
        '<input type="range" min="0" max="%d" step="1" value="0" data-kr-lo aria-label="Диаметр от">'
        '<input type="range" min="0" max="%d" step="1" value="%d" data-kr-hi aria-label="Диаметр до"></div></div>'
        % (diams[0], diams[-1], last, last, last)
        + group('Конструкция', opts('c', present(CONSTR_ORDER, {c['fconstr'] for c in cards})))
        + group('Тип покрытия', opts('k', present(COAT_ORDER, {c['fcoat'] for c in cards})))
        + group('Направление свивки', opts('l', present(LAY_ORDER, {c['flay'] for c in cards})))
        + group('Применение', opts('a', apps))
        + '<div class="kr-side__foot"><button type="button" class="kr-apply" data-kr-close>Применить</button>'
          '<button type="button" class="kr-reset" data-kr-reset>Сбросить</button></div>')

    out = []
    for i, c in enumerate(cards):
        rows = [[r['label'], [apps.index(a) for a in r['apps']]] for r in c['rows']]
        apps_card = [a for a in apps if any(a in r['apps'] for r in c['rows'])]
        d0, d1 = c['rows'][0]['label'], c['rows'][-1]['label']
        rng = d0 if d0 == d1 else '%s–%s' % (d0, d1)
        search = ' '.join([c['code'], c['code'].replace('x', '×'), c['constr'], c['coat'], c['lay'], c['desc'], ' '.join(apps_card)]).lower()
        # без переноса внутри «1960 Н/мм²» и «6,5–10 мм»
        nb = lambda v: v.replace(' ', ' ').replace('/', '/⁠').replace('–', '⁠–⁠')
        text = '%s, свивка %s, %s. Диаметр %s.' % (c['coat'], c['lay'], nb(c['strength']), nb(rng + ' мм'))
        specs = [('Конструкция', c['constr']), ('Количество прядей', c['strands']), ('Сердечник', c['core']),
                 ('Направление свивки', c['dir']), ('Тип свивки', c['kind']), ('Обозначение свивки', c['lay']),
                 ('Покрытие проволоки', c['coating']), ('Некрутящийся канат', c['nonrot']),
                 ('Временное сопротивление разрыву проволоки', c['strength']),
                 ('Применение', ', '.join(apps_card)), ('Сертификаты', c['cert'])]
        dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(k), esc(v)) for k, v in specs)
        adv = ('<ul class="kr-adv">%s</ul>' % ''.join(adv_html(a) for a in c['adv'])) if c['adv'] else ''
        chips = ''.join('<button type="button" class="kr-d" data-kr-d="%s" aria-pressed="false">%s</button>' % (esc(r['label']), esc(r['label'])) for r in c['rows'])
        badge = '<span class="kr-card__badge">Некрутящийся</span>' if c['nonrot'] == 'Да' else ''
        out.append(
            '<article class="kr-card" data-kr-i="%d" data-kr-c="%s" data-kr-k="%s" data-kr-l="%s" data-kr-rows="%s" data-kr-min="%s" data-kr-s="%s">'
            '<button type="button" class="kr-card__ph" data-krd-popup="rope" aria-label="Подробнее: канат %s">%s<img src="%s" alt="" width="72" height="72" loading="lazy"></button>'
            '<h3 class="kr-card__title"><button type="button" data-krd-popup="rope">Канат %s</button></h3>'
            '<p class="kr-card__code">%s</p>'
            '<p class="kr-card__text">%s</p>'
            '<p class="kr-card__price">Цена по запросу</p>'
            '<button class="kr-card__btn" type="button" data-krd-popup="order" data-kr-order data-kc-product="%s">Предзаказ</button>'
            '<div class="kr-info" hidden><p class="kr-info__lead">%s</p>'
            '<div class="kr-diams"><p>Диаметр, мм <span>выберите нужный</span></p><div>%s</div></div>%s'
            '<dl class="kr-specs">%s</dl></div>'
            '</article>' % (
                i, esc(c['fconstr']), esc(c['fcoat']), esc(c['flay']), esc(json.dumps(rows, ensure_ascii=False, separators=(',', ':'))),
                c['rows'][0]['num'], esc(search), esc(c['code']), badge, ICON, esc(c['constr']), esc(c['code']), esc(text),
                esc('Канат ' + c['code']), esc(c['desc']), chips, adv, dl))

    howto = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(a), esc(b)) for a, b in HOWTO)
    where = ''.join('<li><b>%s</b> — %s</li>' % (esc(a), esc(b)) for a, b in WHERE)
    pop = ('<div class="krd-pop kr-pop" id="krd-pop-rope" role="dialog" aria-modal="true" aria-labelledby="kr-pop-t">'
           '<div class="krd-pop__overlay" data-krd-close></div><div class="krd-pop__box">'
           '<button class="krd-pop__close" type="button" aria-label="Закрыть" data-krd-close></button>'
           '<div class="krd-pop__body"><p class="krd-pop__kicker">Стальной канат</p><h3 class="krd-pop__title" id="kr-pop-t" data-kr-pop-title></h3>'
           '<p class="kr-pop__code" data-kr-pop-code></p><div data-kr-pop-body></div>'
           '<button class="krd-btn" type="button" data-krd-popup="order" data-kr-pop-order>Предзаказ</button></div></div></div>')
    layout = (
        '<!--ropes-->\n'
        '<div class="kc-layout kr-layout">\n'
        '<aside class="kr-side" data-kr-side aria-label="Фильтры"><button type="button" class="kr-close" data-kr-close aria-label="Закрыть фильтры"></button>%s</aside>\n'
        '<div class="kc-list">\n'
        '<div class="kc-tools"><label class="kc-search"><input type="search" placeholder="Поиск" '
        'aria-label="Поиск по стальным канатам" data-kc-search></label>'
        '<button type="button" class="kr-open" data-kr-open>Фильтры <span data-kr-active></span></button>'
        '<label class="kc-sort kr-sort"><span>Сортировать по:</span><select aria-label="Сортировать по" data-kc-sort><option value="pop">популярности</option>'
        '<option value="d">диаметру</option><option value="name">названию</option></select></label></div>\n'
        '<div class="kr-bar"><p class="kr-found">Найдено: <b data-kr-total></b></p><div class="kr-picked" data-kr-picked></div></div>\n'
        '<div class="kr-grid">%s</div>\n'
        '<div class="kc-empty"><p>Под эти параметры марок нет. Измените фильтры или оставьте заявку — подберём канат.</p>'
        '<button type="button" data-kc-reset>Сбросить фильтры</button></div>\n'
        '</div>\n</div>\n'
        '<section class="kr-help" aria-label="Подсказки">'
        '<details class="kr-acc" id="kr-howto" open><summary><h2>Как выбрать?</h2>%s</summary><dl class="kr-acc__rows">%s</dl></details>'
        '<details class="kr-acc" id="kr-where" open><summary><h2>Где применяется?</h2>%s</summary><ul class="kr-acc__list">%s</ul></details>'
        '</section>\n%s\n'
        '<!--/ropes-->\n') % (side, ''.join(out), ARROW, howto, ARROW, where, pop)
    sub = ('Для подъёмной, строительной и буровой техники. %d марок, диаметр от %s до %s мм, другие — по запросу.'
           % (len(cards), diams[0], diams[-1]))
    return layout, sub


CSS = r'''
/*ropes*/
.vb-krd .vb-krd-cat .kr-layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:24px;align-items:start}
.vb-krd .kr-side{position:sticky;top:96px;max-height:calc(100vh - 120px);overflow:auto;padding:22px 20px;border-radius:24px;background:#fff;box-shadow:0 10px 30px rgba(32,64,67,.05);scrollbar-width:thin}
.vb-krd .kr-side__title{margin:0 0 4px;font-family:"Montserrat",Arial,sans-serif;font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--kc-head)}
.vb-krd .kr-close,.vb-krd .kr-open{display:none}
.vb-krd .kr-f-group{margin:16px 0 0;padding:16px 0 0;border-top:1px solid var(--kc-line)}
.vb-krd .kr-f-head,.vb-krd .kr-f-group summary{display:flex;align-items:center;justify-content:space-between;margin:0 0 12px;font-size:14px;font-weight:600;color:var(--kc-head);list-style:none;cursor:pointer}
.vb-krd .kr-f-head{cursor:default}
.vb-krd .kr-f-group summary::-webkit-details-marker{display:none}
.vb-krd .kr-f-group summary svg{width:18px;height:18px;color:var(--kc-accent-2);transition:transform .2s}
.vb-krd .kr-f-group:not([open]) summary{margin-bottom:0}
.vb-krd .kr-f-group:not([open]) summary svg{transform:rotate(180deg)}
.vb-krd .kr-range__fields{display:flex;gap:10px;margin:0 0 14px}
.vb-krd .kr-range__fields label{display:flex;align-items:center;gap:8px;flex:1;min-width:0;font-size:13px;color:var(--kc-muted)}
.vb-krd .kr-range__fields input{width:100%;min-width:0;height:34px;padding:0 10px;border:1px solid var(--kc-line);border-radius:10px;background:#f4f8f9;font:inherit;font-size:13px;color:var(--kc-ink);outline:none;transition:border-color .2s}
.vb-krd .kr-range__fields input:focus{border-color:var(--kc-accent-2);background:#fff}
.vb-krd .kr-range{position:relative;height:20px;margin:0 8px 4px}
.vb-krd .kr-range::before{content:"";position:absolute;left:0;right:0;top:9px;height:2px;border-radius:2px;background:var(--kc-line)}
.vb-krd .kr-range__fill{position:absolute;top:9px;height:2px;border-radius:2px;background:var(--kc-accent)}
.vb-krd .kr-range input{position:absolute;left:-8px;right:-8px;top:0;width:calc(100% + 16px);height:20px;margin:0;background:none;pointer-events:none;-webkit-appearance:none;appearance:none}
.vb-krd .kr-range input::-webkit-slider-thumb{width:18px;height:18px;border:2px solid var(--kc-accent);border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(32,64,67,.18);cursor:pointer;pointer-events:auto;-webkit-appearance:none;appearance:none}
.vb-krd .kr-range input::-moz-range-thumb{width:14px;height:14px;border:2px solid var(--kc-accent);border-radius:50%;background:#fff;cursor:pointer;pointer-events:auto}
.vb-krd .kr-range input::-moz-range-track{background:none}
.vb-krd .kr-f-list{list-style:none;margin:0;padding:0}
.vb-krd .kr-f-opt{display:flex;align-items:center;gap:10px;padding:5px 2px;font-size:13px;line-height:1.3;color:var(--kc-ink);cursor:pointer}
.vb-krd .kr-f-opt input{position:absolute;opacity:0;pointer-events:none}
.vb-krd .kr-f-opt i{flex:none;width:18px;height:18px;border:1.5px solid #c3d6d7;border-radius:6px;background:#fff;transition:background-color .2s,border-color .2s}
.vb-krd .kr-f-opt input:checked+i{border-color:var(--kc-accent);background:var(--kc-accent) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 6 9 17l-5-5'/%3E%3C/svg%3E") center/12px no-repeat}
.vb-krd .kr-f-opt input:focus-visible+i{outline:2px solid var(--kc-accent-2);outline-offset:2px}
.vb-krd .kr-f-opt span{flex:1}
.vb-krd .kr-f-opt em{font-style:normal;font-size:12px;color:var(--kc-muted)}
.vb-krd .kr-f-opt:hover span{color:var(--kc-accent)}
.vb-krd .kr-f-opt.is-off{opacity:.35;cursor:default}
.vb-krd .kr-side__foot{display:grid;gap:8px;margin:20px 0 0;padding:16px 0 0;border-top:1px solid var(--kc-line)}
.vb-krd .kr-apply{display:none}
.vb-krd .kr-reset{height:40px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;color:var(--kc-muted);font-size:13px;font-weight:600;cursor:pointer;transition:border-color .2s,color .2s}
.vb-krd .kr-reset:hover{border-color:var(--kc-accent-2);color:var(--kc-accent)}
.vb-krd .kr-bar{display:flex;align-items:center;flex-wrap:wrap;gap:8px 16px;margin:-14px 0 16px}
.vb-krd .kr-found{margin:0;font-size:13px;color:var(--kc-muted)}
.vb-krd .kr-found b{color:var(--kc-head)}
.vb-krd .kr-picked{display:flex;flex-wrap:wrap;gap:6px}
.vb-krd .kr-picked button{display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 10px 0 12px;border:0;border-radius:30px;background:#fff;color:var(--kc-accent);font-size:12px;font-weight:600;cursor:pointer}
.vb-krd .kr-picked button::after{content:"×";font-size:15px;line-height:1}
.vb-krd .kr-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.vb-krd .kr-card{display:flex;flex-direction:column;padding:8px 8px 12px;border-radius:20px;background:#fff;box-shadow:0 10px 30px rgba(32,64,67,.05);transition:box-shadow .25s,transform .25s}
.vb-krd .kr-card[hidden]{display:none}
.vb-krd .kr-card:hover{box-shadow:0 18px 40px rgba(32,64,67,.12);transform:translateY(-2px)}
.vb-krd .kr-card__ph{position:relative;display:flex;align-items:center;justify-content:center;width:100%;aspect-ratio:229/184;margin:0 0 14px;padding:0;border:0;border-radius:14px;background:radial-gradient(120% 100% at 50% 0%,#f3f9f9 0%,#e3eff0 100%);cursor:pointer}
.vb-krd .kr-card__ph img{width:64px;height:64px;border-radius:16px;background:#fff;box-shadow:0 10px 26px rgba(32,64,67,.12);transition:transform .25s}
.vb-krd .kr-card:hover .kr-card__ph img{transform:scale(1.05)}
.vb-krd .kr-card__badge{position:absolute;top:10px;left:10px;padding:4px 10px;border-radius:30px;background:#fff;color:var(--kc-accent);font-size:11px;font-weight:600}
.vb-krd .kr-card__title{margin:0 4px 2px;font-family:"Inter",Arial,sans-serif;font-size:16px;line-height:1.35;font-weight:600}
.vb-krd .kr-card__title button{padding:0;border:0;background:none;color:var(--kc-ink);font:inherit;text-align:left;cursor:pointer;transition:color .2s}
.vb-krd .kr-card__title button:hover{color:var(--kc-accent)}
.vb-krd .kr-card__code{margin:0 4px 8px;font-size:12px;color:var(--kc-muted)}
.vb-krd .kr-card__text{margin:0 4px 12px;font-size:13px;line-height:1.45;color:rgba(32,49,51,.8)}
.vb-krd .kr-card__price{margin:auto 4px 10px;font-size:14px;font-weight:600;color:var(--kc-head)}
.vb-krd .kr-card__btn{height:40px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;color:var(--kc-ink);font-size:13px;font-weight:500;cursor:pointer;transition:background-color .2s,border-color .2s,color .2s}
.vb-krd .kr-card__btn:hover{background:var(--kc-accent);border-color:var(--kc-accent);color:#fff}
.vb-krd .kr-sort{display:flex;align-items:center;height:44px;padding:0 0 0 20px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;font-size:14px;color:var(--kc-muted);cursor:pointer}
.vb-krd .kr-sort span{flex:none;margin-right:4px}
.vb-krd .kr-sort select{height:42px;padding:0 44px 0 0;border:0;background:none;color:var(--kc-ink)}
.vb-krd .kr-help{display:grid;gap:12px;margin:72px 0 0}
.vb-krd .kr-acc{padding:0 32px;border-radius:24px;background:#fff;box-shadow:0 10px 30px rgba(32,64,67,.05)}
.vb-krd .kr-acc summary{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:26px 0;list-style:none;cursor:pointer}
.vb-krd .kr-acc summary::-webkit-details-marker{display:none}
.vb-krd .kr-acc h2{margin:0;font-family:"Montserrat",Arial,sans-serif;font-size:24px;line-height:1.2;font-weight:700;color:var(--kc-head)}
.vb-krd .kr-acc summary svg{flex:none;width:28px;height:28px;padding:5px;border-radius:50%;background:var(--kc-soft);color:var(--kc-accent);transition:transform .2s}
.vb-krd .kr-acc:not([open]) summary svg{transform:rotate(180deg)}
.vb-krd .kr-acc__rows{margin:0;padding:0 0 26px}
.vb-krd .kr-acc__rows div{display:grid;grid-template-columns:200px minmax(0,560px);gap:24px;padding:14px 0;border-top:1px solid var(--kc-line);font-size:14px;line-height:1.55}
.vb-krd .kr-acc__rows dt{font-weight:600;color:var(--kc-head)}
.vb-krd .kr-acc__rows dd{margin:0;color:rgba(32,49,51,.8)}
.vb-krd .kr-acc__list{list-style:none;margin:0;padding:0 0 26px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.vb-krd .kr-acc__list li{padding:14px 16px;border-radius:14px;background:#f4f8f9;font-size:14px;line-height:1.5;color:rgba(32,49,51,.8)}
.vb-krd .kr-acc__list b{font-weight:600;color:var(--kc-head)}
#krd-pops .kr-pop .krd-pop__box{max-width:640px}
#krd-pops .kr-pop__code{margin:-6px 0 16px;font-size:13px;color:#5f7375}
#krd-pops .kr-info__lead{margin:0 0 16px;font-size:14px;line-height:1.55;color:#203133}
#krd-pops .kr-diams{margin:0 0 16px;padding:14px 16px;border-radius:14px;background:#eef5f6}
#krd-pops .kr-diams p{margin:0 0 10px;font-size:13px;font-weight:600;color:#204043}
#krd-pops .kr-diams p span{font-weight:400;color:#5f7375}
#krd-pops .kr-diams div{display:flex;flex-wrap:wrap;gap:6px}
#krd-pops .kr-d{min-width:42px;height:32px;padding:0 10px;border:1px solid #dce7e8;border-radius:30px;background:#fff;color:#203133;font:inherit;font-size:13px;font-weight:500;cursor:pointer;transition:background-color .2s,border-color .2s,color .2s}
#krd-pops .kr-d:hover{border-color:#69979c}
#krd-pops .kr-d[aria-pressed="true"]{background:#457c82;border-color:#457c82;color:#fff}
#krd-pops .kr-adv{list-style:none;margin:0 0 16px;padding:0;display:grid;gap:8px}
#krd-pops .kr-adv li{padding:12px 14px;border-radius:12px;background:#f4f8f9;font-size:13px;line-height:1.5;color:#4f6668}
#krd-pops .kr-adv b{display:block;margin:0 0 2px;color:#204043;font-weight:600}
#krd-pops .kr-specs{margin:0 0 20px}
#krd-pops .kr-specs div{display:grid;grid-template-columns:46% 1fr;gap:12px;padding:8px 0;border-bottom:1px dotted #cfdfe0;font-size:13px;line-height:1.4}
#krd-pops .kr-specs dt{color:#5f7375}
#krd-pops .kr-specs dd{margin:0;color:#203133;font-weight:500}
@media(max-width:959px){
.vb-krd .vb-krd-cat .kr-layout{display:block}
.vb-krd .kr-open{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:44px;padding:0 20px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;color:var(--kc-ink);font-size:14px;font-weight:500;cursor:pointer}
.vb-krd .kr-open span:not(:empty){display:inline-flex;align-items:center;justify-content:center;min-width:20px;height:20px;padding:0 6px;border-radius:20px;background:var(--kc-accent);color:#fff;font-size:11px}
.vb-krd .kr-side{position:fixed;z-index:1000;inset:0;display:none;max-height:none;padding:20px 20px 24px;border-radius:0;overflow:auto}
.vb-krd .kr-side.is-open{display:block}
.vb-krd .kr-close{display:block;position:absolute;top:14px;right:14px;width:36px;height:36px;border:0;border-radius:50%;background:var(--kc-soft);cursor:pointer}
.vb-krd .kr-close::before,.vb-krd .kr-close::after{content:"";position:absolute;left:11px;top:17px;width:14px;height:2px;background:var(--kc-head);transform:rotate(45deg)}
.vb-krd .kr-close::after{transform:rotate(-45deg)}
.vb-krd .kr-side__title{font-size:16px;line-height:36px}
.vb-krd .kr-side__foot{position:sticky;bottom:-24px;margin:20px -20px -24px;padding:12px 20px 20px;background:#fff;box-shadow:0 -8px 20px rgba(32,64,67,.06);grid-template-columns:1fr auto}
.vb-krd .kr-apply{display:block;height:48px;border:0;border-radius:30px;background:var(--kc-accent);color:#fff;font-size:15px;font-weight:600;cursor:pointer}
.vb-krd .kr-reset{height:48px;padding:0 20px}
.vb-krd .kr-bar{margin-top:-8px}
.vb-krd .kr-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.vb-krd .kr-acc__rows div{grid-template-columns:160px 1fr}
}
@media(max-width:639px){
.vb-krd .kr-grid{grid-template-columns:1fr}
.vb-krd .kc-tools{display:grid;grid-template-columns:1fr auto}
.vb-krd .kc-tools .kc-search{grid-column:1/-1}
.vb-krd .kr-sort{padding-left:16px}
.vb-krd .kr-sort span{display:none}
.vb-krd .kr-sort select{padding-right:36px}
.vb-krd .kr-card{display:grid;grid-template-columns:96px minmax(0,1fr);column-gap:14px;align-content:start;padding:10px 10px 12px}
.vb-krd .kr-card__ph{grid-row:1/5;width:96px;height:96px;aspect-ratio:auto;margin:0}
.vb-krd .kr-card__ph img{width:52px;height:52px;border-radius:14px}
.vb-krd .kr-card__badge{top:auto;bottom:6px;left:6px;right:6px;padding:3px 6px;font-size:10px;text-align:center}
.vb-krd .kr-card__title{margin-top:2px;font-size:15px}
.vb-krd .kr-card__text{margin-bottom:8px;font-size:12px}
.vb-krd .kr-card__price{margin:0 4px}
.vb-krd .kr-card__btn{grid-column:1/-1;height:44px;margin-top:12px}
.vb-krd .kr-help{margin-top:48px}
.vb-krd .kr-acc{padding:0 18px;border-radius:20px}
.vb-krd .kr-acc summary{padding:20px 0}
.vb-krd .kr-acc h2{font-size:19px}
.vb-krd .kr-acc__rows div{grid-template-columns:1fr;gap:4px}
.vb-krd .kr-acc__list{grid-template-columns:1fr}
}
/*/ropes*/
'''

JS = r'''
(function () {
  var root = document.getElementById('kd-catalog');
  if (!root) return;
  var wrap = root.querySelector('.kc-wrap');
  function fit() {
    var w = document.documentElement.clientWidth;
    wrap.style.zoom = w >= 960 && w !== 1200 ? String(w / 1200) : '';
  }
  fit();
  window.addEventListener('resize', fit);

  var grid = root.querySelector('.kr-grid');
  var cards = [].slice.call(root.querySelectorAll('.kr-card'));
  var search = root.querySelector('[data-kc-search]');
  var sort = root.querySelector('[data-kc-sort]');
  var empty = root.querySelector('.kc-empty');
  var side = root.querySelector('[data-kr-side]');
  var picked = root.querySelector('[data-kr-picked]');
  var boxes = [].slice.call(root.querySelectorAll('input[data-kr-f]'));
  var lo = root.querySelector('[data-kr-lo]'), hi = root.querySelector('[data-kr-hi]');
  var from = root.querySelector('[data-kr-from]'), to = root.querySelector('[data-kr-to]');
  var fill = root.querySelector('[data-kr-fill]');
  var GROUPS = ['c', 'k', 'l', 'a'];
  var APPS = boxes.filter(function (el) { return el.getAttribute('data-kr-f') === 'a'; }).map(function (el) { return el.getAttribute('data-kr-v'); });

  // все диаметры по возрастанию — шаги ползунка
  var DIAMS = [];
  var data = cards.map(function (c) {
    var rows = JSON.parse(c.getAttribute('data-kr-rows')).map(function (r) {
      var n = parseFloat(r[0].replace(',', '.'));
      if (DIAMS.indexOf(n) === -1) DIAMS.push(n);
      return { d: r[0], n: n, a: r[1].map(function (i) { return APPS[i]; }) };
    });
    return {
      el: c, i: +c.getAttribute('data-kr-i'), min: parseFloat(c.getAttribute('data-kr-min')),
      name: c.querySelector('.kr-card__code').textContent,
      c: c.getAttribute('data-kr-c'), k: c.getAttribute('data-kr-k'), l: c.getAttribute('data-kr-l'),
      s: c.getAttribute('data-kr-s'), rows: rows
    };
  });
  DIAMS.sort(function (a, b) { return a - b; });
  var LAST = DIAMS.length - 1;
  function label(n) { return String(n).replace('.', ','); }

  // pop «Подробнее» живёт среди поп-апов сайта, иначе на него не действуют их стили
  // (контейнер #krd-pops стоит ниже скрипта, поэтому переносим при открытии)
  var pop = document.getElementById('krd-pop-rope');
  function home() {
    var pops = document.getElementById('krd-pops');
    if (pop && pops && pop.parentNode !== pops) pops.appendChild(pop);
  }
  var popCard = null;

  function state() {
    var f = { lo: DIAMS[+lo.value], hi: DIAMS[+hi.value] };
    GROUPS.forEach(function (g) { f[g] = []; });
    boxes.forEach(function (el) { if (el.checked) f[el.getAttribute('data-kr-f')].push(el.getAttribute('data-kr-v')); });
    return f;
  }
  function has(list, v) { return list.indexOf(v) !== -1; }
  function rowsOk(x, f) {
    return x.rows.filter(function (r) {
      if (f.lo > r.n || r.n > f.hi) return false;
      if (f.a.length && !f.a.some(function (a) { return has(r.a, a); })) return false;
      return true;
    });
  }
  function query() {
    var q = (search.value || '').trim().toLowerCase();
    return [q, q.replace(/[х×]/g, 'x')];
  }
  function match(x, f, q) {
    if (q[0] && x.s.indexOf(q[0]) === -1 && x.s.indexOf(q[1]) === -1) return false;
    if (f.c.length && !has(f.c, x.c)) return false;
    if (f.k.length && !has(f.k, x.k)) return false;
    if (f.l.length && !has(f.l, x.l)) return false;
    return rowsOk(x, f).length > 0;
  }
  function plural(n) {
    var a = n % 10, b = n % 100;
    if (b >= 11 && 14 >= b) return n + ' марок';
    if (a === 1) return n + ' марка';
    if (a >= 2 && 4 >= a) return n + ' марки';
    return n + ' марок';
  }
  function chip(text, act) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = text;
    b.addEventListener('click', act);
    picked.appendChild(b);
  }

  function paintRange() {
    var a = +lo.value, b = +hi.value;
    fill.style.left = (a / LAST * 100) + '%';
    fill.style.right = (100 - b / LAST * 100) + '%';
    from.value = label(DIAMS[a]);
    to.value = label(DIAMS[b]);
  }

  function apply() {
    var f = state(), q = query(), shown = 0;
    data.forEach(function (x) {
      var ok = match(x, f, q);
      x.el.hidden = !ok;
      if (ok) shown++;
    });
    boxes.forEach(function (el) {
      var g = el.getAttribute('data-kr-f'), v = el.getAttribute('data-kr-v');
      var f2 = { lo: f.lo, hi: f.hi };
      GROUPS.forEach(function (k) { f2[k] = k === g ? [v] : f[k]; });
      var n = data.filter(function (x) { return match(x, f2, q); }).length;
      var lab = el.closest('.kr-f-opt');
      lab.querySelector('[data-kr-n]').textContent = n;
      lab.classList.toggle('is-off', !n && !el.checked);
      el.disabled = !n && !el.checked;
    });
    picked.textContent = '';
    var total = 0;
    if (+lo.value !== 0 || +hi.value !== LAST) {
      total++;
      chip('Ø ' + label(f.lo) + '–' + label(f.hi) + ' мм', function () { lo.value = 0; hi.value = LAST; paintRange(); apply(); });
    }
    boxes.forEach(function (el) {
      if (!el.checked) return;
      total++;
      chip(el.getAttribute('data-kr-v'), function () { el.checked = false; apply(); });
    });
    root.querySelectorAll('[data-kr-total]').forEach(function (el) { el.textContent = plural(shown); });
    root.querySelector('[data-kr-active]').textContent = total ? total : '';
    root.querySelector('.kr-apply').textContent = 'Показать ' + plural(shown);
    empty.classList.toggle('is-shown', !shown);
  }

  function order() {
    var by = sort.value;
    data.slice().sort(function (a, b) {
      if (by === 'name') return a.name.localeCompare(b.name, 'ru');
      if (by === 'd') return a.min - b.min || a.i - b.i;
      return a.i - b.i;
    }).forEach(function (x) { grid.appendChild(x.el); });
  }

  function reset() {
    boxes.forEach(function (el) { el.checked = false; });
    lo.value = 0; hi.value = LAST;
    search.value = '';
    paintRange();
    apply();
  }

  // ввод «От / До»: ближайший диаметр из таблицы
  function snap(input, isLo) {
    var v = parseFloat(String(input.value).replace(',', '.'));
    if (isNaN(v)) { paintRange(); return; }
    var best = 0;
    DIAMS.forEach(function (d, i) { if (Math.abs(d - v) + 0 > Math.abs(DIAMS[best] - v)) return; best = i; });
    if (isLo) lo.value = Math.min(best, +hi.value); else hi.value = Math.max(best, +lo.value);
    paintRange();
    apply();
  }

  function setOrder(btn, product) {
    var p = document.getElementById('krd-pop-order');
    if (!p) return;
    var field = p.querySelector('[data-kc-target]'), lab = p.querySelector('[data-kc-label]');
    if (field) field.value = product;
    if (lab) lab.textContent = product;
  }

  function openSide(on) {
    side.classList.toggle('is-open', on);
    document.documentElement.style.overflow = on ? 'hidden' : '';
  }

  function showHelp(id) {
    var d = document.getElementById(id);
    if (!d) return;
    d.open = true;
    var top = d.getBoundingClientRect().top + window.pageYOffset - 110;
    window.scrollTo({ top: top, behavior: 'smooth' });
  }

  root.addEventListener('click', function (e) {
    var t = e.target;
    var card = t.closest('.kr-card');
    if (card && t.closest('[data-krd-popup="rope"]') && pop) {
      home();
      popCard = card;
      pop.querySelector('[data-kr-pop-title]').textContent = card.querySelector('.kr-card__title').textContent;
      pop.querySelector('[data-kr-pop-code]').textContent = card.querySelector('.kr-card__code').textContent;
      pop.querySelector('[data-kr-pop-body]').innerHTML = card.querySelector('.kr-info').innerHTML;
      return;
    }
    var ord = t.closest('[data-kr-order]');
    if (ord) { setOrder(ord, ord.getAttribute('data-kc-product')); return; }
    if (t.closest('[data-kr-reset]') || t.closest('[data-kc-reset]')) { reset(); return; }
    if (t.closest('[data-kr-open]')) { openSide(true); return; }
    if (t.closest('[data-kr-close]')) { openSide(false); return; }
    var jump = t.closest('[data-kr-jump]');
    if (jump) { showHelp(jump.getAttribute('data-kr-jump')); return; }
    if (t.closest('[data-kc-back]')) {
      if (document.referrer && document.referrer.indexOf(location.host) !== -1) history.back();
      else location.href = window.KRD_SITE_URL ? window.KRD_SITE_URL('/') : '/';
    }
  });

  if (pop) pop.addEventListener('click', function (e) {
    var d = e.target.closest('.kr-d');
    if (d) {
      var on = d.getAttribute('aria-pressed') !== 'true';
      [].forEach.call(pop.querySelectorAll('.kr-d'), function (b) { b.setAttribute('aria-pressed', 'false'); });
      d.setAttribute('aria-pressed', on ? 'true' : 'false');
      return;
    }
    if (e.target.closest('[data-kr-pop-order]') && popCard) {
      var sel = pop.querySelector('.kr-d[aria-pressed="true"]');
      var base = popCard.querySelector('[data-kr-order]').getAttribute('data-kc-product');
      setOrder(null, base + (sel ? ', Ø ' + sel.getAttribute('data-kr-d') + ' мм' : ''));
    }
  });

  root.addEventListener('change', function (e) { if (e.target.closest('input[data-kr-f]')) apply(); });
  lo.addEventListener('input', function () { if (+lo.value > +hi.value) lo.value = hi.value; paintRange(); apply(); });
  hi.addEventListener('input', function () { if (+lo.value > +hi.value) hi.value = lo.value; paintRange(); apply(); });
  from.addEventListener('change', function () { snap(from, true); });
  to.addEventListener('change', function () { snap(to, false); });
  [from, to].forEach(function (el) {
    el.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); el.blur(); } });
  });
  search.addEventListener('input', apply);
  sort.addEventListener('change', order);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && side.classList.contains('is-open')) openSide(false); });
  paintRange();
  apply();
})();
'''


def main():
    cards = load()
    layout, sub = build(cards)
    s = open(DOC, encoding='utf-8').read()
    if '<!--ropes-->' in s:
        a = s.index('<!--ropes-->'); b = s.index('<!--/ropes-->') + len('<!--/ropes-->\n')
    else:
        a = s.index('<div class="kc-layout">'); b = s.index('<section class="kc-cta">')
    s = s[:a] + layout + s[b:]
    s = re.sub(r'(<p class="kc-sub">)[^<]*(</p>)', lambda m: m.group(1) + sub + m.group(2), s, count=1)
    # «Как выбрать?» и «Где применяется?» ведут к блокам под каталогом, как в прототипе
    s = s.replace('<button type="button" data-krd-popup="howto">', '<button type="button" data-kr-jump="kr-howto">')
    s = s.replace('<button type="button" data-krd-popup="where">', '<button type="button" data-kr-jump="kr-where">')
    if '/*ropes*/' in s:
        s = re.sub(r'\n?/\*ropes\*/.*?/\*/ropes\*/\n?', '\n', s, flags=re.S)
    i = s.index('</style>')
    s = s[:i].rstrip('\n') + '\n' + CSS.strip('\n') + '\n' + s[i:]
    a = s.index('<script>') + len('<script>'); b = s.index('</script>', a)
    s = s[:a] + JS + s[b:]
    open(DOC, 'w', encoding='utf-8', newline='\n').write(s)

    assert '<' not in JS, 'в скрипте не должно быть «<»'
    print('== стальные канаты: марок %d, строк %d' % (len(cards), sum(len(c['rows']) for c in cards)))
    if FIXES:
        print('Замечания к таблице (на сайте уже исправлено):')
        for f in FIXES:
            print('  -', f)
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'tilda_block.py'), '--doc', 'steel-ropes'], check=True)
    subprocess.run(['node', os.path.join(ROOT, 'tools', 'product_page.mjs')], check=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
