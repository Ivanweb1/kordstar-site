# Страница «Стальные канаты» из таблицы data/steel-ropes.xlsx.
# Запуск: python tools/ropes_page.py  → обновляет tilda/_doc_steel-ropes.html, затем собирает
# tilda/steel-ropes.html, превью и steel-ropes.html для GitHub Pages (через tilda_block.py и product_page.mjs).
#
# Одна строка таблицы — один диаметр. На сайте одна карточка на марку (полный код, например
# 35WxK7-zZ-Galv-2160) со списком диаметров. Фильтры: диаметр, конструкция, покрытие, направление свивки,
# применение. Применение задаётся у каждого диаметра отдельно, поэтому фильтр проверяет строки, а не марку.
import html, json, os, re, subprocess, sys
from collections import OrderedDict

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, 'data', 'steel-ropes.xlsx')
DOC = os.path.join(ROOT, 'tilda', '_doc_steel-ropes.html')
ICON = 'img/Frame_2136139848-32303965.webp'
FIXES = []  # что поправили в данных — печатаем в конце


def norm_x(s):
    """6x19W / 35WxK7 → 6×19W / 35W×K7 (латинская x и кириллическая х между цифрами/буквами)."""
    return re.sub(r'(?<=[0-9A-Za-z])[xх×](?=[0-9A-Za-z])', '×', s)


def diam(v):
    if isinstance(v, (int, float)):
        v = ('%g' % v).replace('.', ',')
    v = str(v).strip().replace('.', ',')
    num = float(v.replace(',', '.'))
    label = ('%g' % num).replace('.', ',')
    return num, label


APP_FIX = {'Ратяжки': 'Растяжки', 'Растяжка': 'Растяжки'}
LAY = {'sZ': ('Правая', 'Крестовая'), 'zZ': ('Правая', 'Односторонняя'),
       'sS': ('Левая', 'Односторонняя'), 'zS': ('Левая', 'Крестовая')}
LABELS = {'Galv (оцинкованный)': 'Оцинкованный (Galv)', 'Ung (неоцинкованный)': 'Без покрытия (Ung)',
          'sZ (RHRL)': 'sZ — правая крестовая', 'zZ (RHLL)': 'zZ — правая односторонняя',
          'sS (LHLL)': 'sS — левая односторонняя', 'zS (LHRL)': 'zS — левая крестовая'}
LAY_FILTER = {'sZ': 'sZ (RHRL)', 'zZ': 'zZ (RHLL)', 'sS': 'sS (LHLL)', 'zS': 'zS (LHRL)'}


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
            FIXES.append('строка %d: диаметр %r записан числом → «%s»' % (n, r[0], label + ',0'))
        apps = []
        for a in str(r[5]).split(','):
            a = a.strip()
            if not a:
                continue
            if a in APP_FIX:
                FIXES.append('строка %d: «%s» → «%s»' % (n, a, APP_FIX[a]))
                a = APP_FIX[a]
            if a != 'Иное' and a not in apps:
                apps.append(a)
        lay = r[12]
        dir_, kind = LAY[lay]
        if r[10] != dir_:
            FIXES.append('строка %d (%s, %s мм): направление свивки «%s», а по обозначению %s — «%s»' % (n, code, label, r[10], lay, dir_))
        core = r[9]
        if 'PWRC' in code and 'PWRC' not in core:
            FIXES.append('строка %d (%s, %s мм): сердечник «%s», а в марке PWRC(K)' % (n, code, label, core))
            core = 'Стальной с пластически обжатыми прядями (PWRC(K))'
        nonrot = str(r[14]).capitalize()
        if r[14] != nonrot:
            FIXES.append('строка %d: «%s» → «%s» (некрутящийся)' % (n, r[14], nonrot))
        constr = norm_x(r[8])
        filt_constr = norm_x(r[2]).replace(', ГОСТ', ' (ГОСТ') + (')' if 'ГОСТ' in r[2] else '')
        c = cards.get(code)
        if c is None:
            galv = 'Galv' in r[3]
            c = cards[code] = dict(
                code=norm_x(code), constr=constr, fconstr=filt_constr,
                coat='Оцинкованный' if galv else 'Без покрытия', fcoat=r[3],
                lay=lay, flay=LAY_FILTER[lay], dir=dir_, kind=kind, core=core,
                strands=str(r[7]), nonrot=nonrot, strength=r[15],
                coating=('Оцинкованная' if galv else 'Неоцинкованная'),
                desc=r[16], adv=[a for a in (r[17], r[18], r[19]) if a], cert=r[20] or 'По запросу',
                rows=[], first=n)
        if any(x['label'] == label for x in c['rows']):
            FIXES.append('строка %d: %s, %s мм — повтор, оставлена одна строка' % (n, code, label))
            continue
        c['rows'].append(dict(num=num, label=label, apps=apps))
    for c in cards.values():
        c['rows'].sort(key=lambda x: x['num'])
    return list(cards.values())


def esc(s):
    return html.escape(str(s), quote=True)


def adv_html(a):
    # «Заголовок. Пояснение.» → жирный заголовок + текст
    m = re.match(r'([^.]+\.)\s*(.*)', a)
    return '<li><b>%s</b> %s</li>' % (esc(m.group(1)), esc(m.group(2))) if m else '<li>%s</li>' % esc(a)


def build(cards):
    apps_all, diams_all = [], {}
    for c in cards:
        for r in c['rows']:
            diams_all[r['label']] = r['num']
            for a in r['apps']:
                if a not in apps_all:
                    apps_all.append(a)
    app_order = ['Башенный кран', 'Автокран', 'Гусеничный кран', 'Мостовой кран', 'Козловые краны', 'Манипулятор',
                 'Эвакуатор', 'Трубоукладчик', 'Буровая установка', 'Лебедка', 'Растяжки']
    apps_all.sort(key=lambda a: app_order.index(a) if a in app_order else 99)
    diams = sorted(diams_all, key=lambda k: diams_all[k])

    def uniq(key, order=None):
        seen = []
        for c in cards:
            if c[key] not in seen:
                seen.append(c[key])
        return sorted(seen, key=order) if order else seen

    def constr_key(s):
        m = re.match(r'(\d+)', s)
        return (int(m.group(1)) if m else 0, s)

    groups = [
        ('d', 'Диаметр, мм', diams, 'chips'),
        ('c', 'Конструкция', uniq('fconstr', constr_key), 'list'),
        ('k', 'Покрытие', uniq('fcoat'), 'list'),
        ('l', 'Направление свивки', [LAY_FILTER[k] for k in ('sZ', 'zZ', 'sS', 'zS') if any(c['lay'] == k for c in cards)], 'list'),
        ('a', 'Применение', apps_all, 'list'),
    ]
    # фильтры
    side = []
    for gid, title, opts, kind in groups:
        if kind == 'chips':
            items = ''.join('<button type="button" class="kr-f-chip" data-kr-f="%s" data-kr-v="%s" aria-pressed="false">%s</button>'
                            % (gid, esc(o), esc(o)) for o in opts)
            body = '<div class="kr-f-chips">%s</div>' % items
        else:
            items = ''.join('<li><label class="kr-f-opt"><input type="checkbox" data-kr-f="%s" data-kr-v="%s"><i></i>'
                            '<span>%s</span><em data-kr-n></em></label></li>' % (gid, esc(o), esc(LABELS.get(o, o))) for o in opts)
            body = '<ul class="kr-f-list">%s</ul>' % items
        side.append('<div class="kr-f-group"><p class="kr-f-title">%s</p>%s</div>' % (title, body))

    # карточки
    out = []
    for i, c in enumerate(cards):
        rows = [[r['label'], [apps_all.index(a) for a in r['apps']]] for r in c['rows']]
        apps_card = [a for a in apps_all if any(a in r['apps'] for r in c['rows'])]
        search = ' '.join([c['code'], c['code'].replace('×', 'x'), c['constr'], c['coat'], c['lay'], c['desc'], ' '.join(apps_card)]).lower()
        tags = ['<li>%s</li>' % c['coat'], '<li>Свивка %s</li>' % c['lay'], '<li>%s</li>' % esc(c['strength'])]
        if c['nonrot'] == 'Да':
            tags.append('<li class="is-accent">Некрутящийся</li>')
        chips = ''.join('<button type="button" class="kr-d" data-kr-d="%s" aria-pressed="false">%s</button>' % (esc(r['label']), esc(r['label'])) for r in c['rows'])
        specs = [('Конструкция', c['constr']), ('Количество прядей', c['strands']), ('Сердечник', c['core']),
                 ('Направление свивки', c['dir']), ('Тип свивки', c['kind']), ('Обозначение свивки', c['lay']),
                 ('Покрытие проволоки', c['coating']), ('Некрутящийся канат', c['nonrot']),
                 ('Временное сопротивление разрыву', c['strength']),
                 ('Диаметры, мм', ', '.join(r['label'] for r in c['rows'])),
                 ('Применение', ', '.join(apps_card)), ('Сертификаты', c['cert'])]
        dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(k), esc(v)) for k, v in specs)
        adv = ('<ul class="kr-adv">%s</ul>' % ''.join(adv_html(a) for a in c['adv'])) if c['adv'] else ''
        d0 = c['rows'][0]['label']; d1 = c['rows'][-1]['label']
        rng = d0 if d0 == d1 else '%s–%s' % (d0, d1)
        out.append(
            '<article class="kr-card" data-kr-i="%d" data-kr-c="%s" data-kr-k="%s" data-kr-l="%s" data-kr-rows="%s" data-kr-min="%s" data-kr-s="%s">'
            '<div class="kr-card__head"><span class="kr-card__ico"><img src="%s" alt="" width="72" height="72" loading="lazy"></span>'
            '<div><h3 class="kr-card__title">Канат %s</h3><p class="kr-card__code">%s</p></div></div>'
            '<ul class="kr-tags">%s</ul>'
            '<p class="kr-card__text">%s</p>'
            '<div class="kr-diams"><p>Диаметр, мм <span>%s · выберите нужный</span></p><div>%s</div></div>'
            '<details class="kr-more"><summary>Характеристики и преимущества</summary>%s<dl class="kr-specs">%s</dl></details>'
            '<div class="kr-card__foot"><span class="kr-card__price">Цена по запросу</span>'
            '<button class="kr-card__btn" type="button" data-krd-popup="order" data-kr-order data-kc-product="%s">Предзаказ</button></div>'
            '</article>' % (
                i, esc(c['fconstr']), esc(c['fcoat']), esc(c['flay']), esc(json.dumps(rows, ensure_ascii=False, separators=(',', ':'))),
                c['rows'][0]['num'], esc(search), ICON, esc(c['constr']), esc(c['code']), ''.join(tags), esc(c['desc']),
                esc(rng), chips, adv, dl, esc('Канат ' + c['code'])))

    lo = diams[0]; hi = diams[-1]
    layout = (
        '<!--ropes-->\n'
        '<div class="kc-layout kr-layout">\n'
        '<aside class="kc-side kr-side" data-kr-side aria-label="Фильтры"><div class="kr-side__head"><p class="kc-side__title">Фильтры</p>'
        '<button type="button" class="kr-reset" data-kr-reset hidden>Сбросить</button>'
        '<button type="button" class="kr-close" data-kr-close aria-label="Закрыть фильтры"></button></div>%s'
        '<button type="button" class="kr-apply" data-kr-close>Показать <span data-kr-total></span></button></aside>\n'
        '<div class="kc-list">\n'
        '<div class="kc-tools"><label class="kc-search"><input type="search" placeholder="Поиск: 35WxK7, оцинкованный, автокран" '
        'aria-label="Поиск по стальным канатам" data-kc-search></label>'
        '<button type="button" class="kr-open" data-kr-open>Фильтры <span data-kr-active></span></button>'
        '<label class="kc-sort"><select aria-label="Сортировка" data-kc-sort><option value="pop">По умолчанию</option>'
        '<option value="d">По диаметру</option><option value="name">По названию, А–Я</option></select></label></div>\n'
        '<div class="kr-bar"><p class="kr-found">Найдено: <b data-kr-total></b></p><div class="kr-picked" data-kr-picked></div></div>\n'
        '<div class="kr-grid">%s</div>\n'
        '<div class="kc-empty"><p>Под эти параметры марок нет. Измените фильтры или оставьте заявку — подберём канат.</p>'
        '<button type="button" data-kc-reset>Сбросить фильтры</button></div>\n'
        '</div>\n</div>\n<!--/ropes-->\n') % (''.join(side), ''.join(out))
    sub = ('Для подъёмной, строительной и буровой техники. %d марок, диаметр от %s до %s мм, другие — по запросу.'
           % (len(cards), lo, hi))
    return layout, sub


CSS = r'''
/*ropes*/
.vb-krd .vb-krd-cat .kr-layout{display:grid;grid-template-columns:248px minmax(0,1fr);gap:24px;align-items:start}
.vb-krd .kr-side{padding:20px 18px 22px;max-height:calc(100vh - 120px);overflow:auto;scrollbar-width:thin}
.vb-krd .kr-side__head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:0 0 6px}
.vb-krd .kr-side__head .kc-side__title{margin:0}
.vb-krd .kr-reset{padding:0;border:0;background:none;color:var(--kc-accent);font-size:13px;font-weight:600;cursor:pointer}
.vb-krd .kr-reset[hidden],.vb-krd .kr-close,.vb-krd .kr-apply,.vb-krd .kr-open{display:none}
.vb-krd .kr-f-group{padding:16px 0 0;margin:14px 0 0;border-top:1px solid var(--kc-line)}
.vb-krd .kr-f-title{margin:0 0 10px;font-size:13px;font-weight:700;color:var(--kc-head)}
.vb-krd .kr-f-chips{display:flex;flex-wrap:wrap;gap:6px}
.vb-krd .kr-f-chip{min-width:38px;height:30px;padding:0 9px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;color:var(--kc-ink);font-size:12px;font-weight:500;cursor:pointer;transition:background-color .2s,border-color .2s,color .2s}
.vb-krd .kr-f-chip:hover{border-color:var(--kc-accent-2)}
.vb-krd .kr-f-chip[aria-pressed="true"]{background:var(--kc-accent);border-color:var(--kc-accent);color:#fff}
.vb-krd .kr-f-chip:disabled,.vb-krd .kr-f-opt.is-off{opacity:.35;cursor:default}
.vb-krd .kr-f-list{list-style:none;margin:0;padding:0}
.vb-krd .kr-f-opt{display:flex;align-items:center;gap:10px;padding:6px 4px;border-radius:10px;font-size:13px;line-height:1.3;color:var(--kc-ink);cursor:pointer}
.vb-krd .kr-f-opt input{position:absolute;opacity:0;pointer-events:none}
.vb-krd .kr-f-opt i{flex:none;width:18px;height:18px;border:1.5px solid #c3d6d7;border-radius:6px;background:#fff;transition:background-color .2s,border-color .2s}
.vb-krd .kr-f-opt input:checked+i{border-color:var(--kc-accent);background:var(--kc-accent) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 6 9 17l-5-5'/%3E%3C/svg%3E") center/12px no-repeat}
.vb-krd .kr-f-opt input:focus-visible+i{outline:2px solid var(--kc-accent-2);outline-offset:2px}
.vb-krd .kr-f-opt span{flex:1}
.vb-krd .kr-f-opt em{font-style:normal;font-size:12px;color:var(--kc-muted)}
.vb-krd .kr-f-opt:hover span{color:var(--kc-accent)}
.vb-krd .kr-bar{display:flex;align-items:center;flex-wrap:wrap;gap:8px 16px;margin:-12px 0 16px}
.vb-krd .kr-found{margin:0;font-size:14px;color:var(--kc-muted)}
.vb-krd .kr-found b{color:var(--kc-head)}
.vb-krd .kr-picked{display:flex;flex-wrap:wrap;gap:6px}
.vb-krd .kr-picked button{display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 10px 0 12px;border:0;border-radius:30px;background:var(--kc-soft);color:var(--kc-accent);font-size:12px;font-weight:600;cursor:pointer}
.vb-krd .kr-picked button::after{content:"×";font-size:15px;line-height:1}
.vb-krd .kr-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start}
.vb-krd .kr-card{display:flex;flex-direction:column;padding:20px;border-radius:20px;background:#fff;box-shadow:0 10px 30px rgba(32,64,67,.05);transition:box-shadow .25s}
.vb-krd .kr-card[hidden]{display:none}
.vb-krd .kr-card:hover{box-shadow:0 18px 40px rgba(32,64,67,.1)}
.vb-krd .kr-card__head{display:flex;align-items:center;gap:14px;margin:0 0 14px}
.vb-krd .kr-card__ico{flex:none;display:flex;width:52px;height:52px;border-radius:14px;overflow:hidden}
.vb-krd .kr-card__ico img{width:100%;height:100%}
.vb-krd .kr-card__title{margin:0 0 3px;font-family:"Montserrat",Arial,sans-serif;font-size:17px;line-height:1.2;font-weight:700;color:var(--kc-head)}
.vb-krd .kr-card__code{margin:0;font-size:12px;color:var(--kc-muted);letter-spacing:.02em}
.vb-krd .kr-tags{display:flex;flex-wrap:wrap;gap:6px;list-style:none;margin:0 0 12px;padding:0}
.vb-krd .kr-tags li{padding:5px 10px;border-radius:30px;background:#f3f8f8;font-size:12px;font-weight:500;color:#4f6668}
.vb-krd .kr-tags li.is-accent{background:var(--kc-soft);color:var(--kc-accent);font-weight:600}
.vb-krd .kr-card__text{margin:0 0 14px;font-size:13px;line-height:1.5;color:rgba(32,49,51,.8)}
.vb-krd .kr-diams p{margin:0 0 8px;font-size:12px;font-weight:600;color:var(--kc-head)}
.vb-krd .kr-diams p span{font-weight:400;color:var(--kc-muted)}
.vb-krd .kr-diams div{display:flex;flex-wrap:wrap;gap:6px}
.vb-krd .kr-d{min-width:40px;height:30px;padding:0 9px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;color:var(--kc-ink);font-size:12px;font-weight:500;cursor:pointer;transition:background-color .2s,border-color .2s,color .2s,opacity .2s}
.vb-krd .kr-d:hover{border-color:var(--kc-accent-2)}
.vb-krd .kr-d.is-dim{opacity:.35}
.vb-krd .kr-d[aria-pressed="true"]{background:var(--kc-accent);border-color:var(--kc-accent);color:#fff;opacity:1}
.vb-krd .kr-more{margin:14px 0 0;border-top:1px solid var(--kc-line)}
.vb-krd .kr-more summary{display:flex;align-items:center;justify-content:space-between;padding:12px 0 0;color:var(--kc-accent);font-size:13px;font-weight:600;cursor:pointer;list-style:none}
.vb-krd .kr-more summary::-webkit-details-marker{display:none}
.vb-krd .kr-more summary::after{content:"";width:7px;height:7px;margin-right:4px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg);transition:transform .2s}
.vb-krd .kr-more[open] summary::after{transform:rotate(-135deg)}
.vb-krd .kr-adv{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:8px}
.vb-krd .kr-adv li{padding:10px 12px;border-radius:12px;background:#f3f8f8;font-size:12px;line-height:1.5;color:#4f6668}
.vb-krd .kr-adv b{display:block;margin:0 0 2px;color:var(--kc-head);font-weight:600}
.vb-krd .kr-specs{margin:12px 0 0}
.vb-krd .kr-specs div{display:grid;grid-template-columns:44% 1fr;gap:10px;padding:7px 0;border-bottom:1px dotted #cfdfe0;font-size:12px;line-height:1.4}
.vb-krd .kr-specs dt{color:var(--kc-muted)}
.vb-krd .kr-specs dd{margin:0;color:var(--kc-ink);font-weight:500}
.vb-krd .kr-card__foot{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:16px 0 0;padding:16px 0 0;border-top:1px solid var(--kc-line)}
.vb-krd .kr-card__price{font-size:13px;font-weight:600;color:var(--kc-head)}
.vb-krd .kr-card__btn{height:40px;padding:0 24px;border:1px solid var(--kc-accent);border-radius:30px;background:var(--kc-accent);color:#fff;font-size:13px;font-weight:500;cursor:pointer;transition:background-color .2s}
.vb-krd .kr-card__btn:hover{background:#3a6a6f}
@media(max-width:959px){
.vb-krd .vb-krd-cat .kr-layout{display:block}
.vb-krd .kr-open{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:44px;padding:0 20px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;color:var(--kc-ink);font-size:14px;font-weight:500;cursor:pointer}
.vb-krd .kr-open span:not(:empty){display:inline-flex;align-items:center;justify-content:center;min-width:20px;height:20px;padding:0 6px;border-radius:20px;background:var(--kc-accent);color:#fff;font-size:11px}
.vb-krd .kc-side.kr-side{position:fixed;z-index:1000;inset:0;display:none;max-height:none;padding:20px 20px 96px;border-radius:0;overflow:auto}
.vb-krd .kc-side.kr-side.is-open{display:block}
.vb-krd .kr-close{display:block;width:36px;height:36px;margin-left:auto;border:0;border-radius:50%;background:var(--kc-soft);cursor:pointer;position:relative}
.vb-krd .kr-close::before,.vb-krd .kr-close::after{content:"";position:absolute;left:11px;top:17px;width:14px;height:2px;background:var(--kc-head);transform:rotate(45deg)}
.vb-krd .kr-close::after{transform:rotate(-45deg)}
.vb-krd .kr-apply{display:block;position:fixed;left:20px;right:20px;bottom:20px;height:52px;border:0;border-radius:30px;background:var(--kc-accent);color:#fff;font-size:15px;font-weight:600;cursor:pointer}
.vb-krd .kr-bar{margin-top:-8px}
}
@media(max-width:639px){
.vb-krd .kr-grid{grid-template-columns:1fr}
.vb-krd .kc-tools{display:grid;grid-template-columns:1fr auto}
.vb-krd .kc-tools .kc-search{grid-column:1/-1}
.vb-krd .kr-card{padding:16px}
.vb-krd .kr-card__foot{flex-direction:column;align-items:stretch}
.vb-krd .kr-card__btn{height:44px}
}
@media(min-width:640px) and (max-width:959px){.vb-krd .kr-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
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
  var inputs = [].slice.call(root.querySelectorAll('[data-kr-f]'));
  var GROUPS = ['d', 'c', 'k', 'l', 'a'];
  // применение в data-kr-rows хранится индексами — в том же порядке, что и в фильтре
  var APPS = [].slice.call(root.querySelectorAll('[data-kr-f="a"]')).map(function (el) { return el.getAttribute('data-kr-v'); });

  var data = cards.map(function (c) {
    return {
      el: c, i: +c.getAttribute('data-kr-i'), min: parseFloat(c.getAttribute('data-kr-min')),
      name: c.querySelector('.kr-card__code').textContent,
      c: c.getAttribute('data-kr-c'), k: c.getAttribute('data-kr-k'), l: c.getAttribute('data-kr-l'),
      s: c.getAttribute('data-kr-s'),
      rows: JSON.parse(c.getAttribute('data-kr-rows')).map(function (r) {
        return { d: r[0], a: r[1].map(function (n) { return APPS[n]; }) };
      })
    };
  });

  function selected() {
    var f = {};
    GROUPS.forEach(function (g) { f[g] = []; });
    inputs.forEach(function (el) {
      var on = el.type === 'checkbox' ? el.checked : el.getAttribute('aria-pressed') === 'true';
      if (on) f[el.getAttribute('data-kr-f')].push(el.getAttribute('data-kr-v'));
    });
    return f;
  }
  function has(list, v) { return list.indexOf(v) !== -1; }
  // строки марки, подходящие под диаметр и применение
  function rowsOk(x, f) {
    return x.rows.filter(function (r) {
      if (f.d.length && !has(f.d, r.d)) return false;
      if (f.a.length && !f.a.some(function (a) { return has(r.a, a); })) return false;
      return true;
    });
  }
  function match(x, f, q) {
    if (q && x.s.indexOf(q) === -1) return false;
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

  function apply() {
    var f = selected();
    var q = (search.value || '').trim().toLowerCase().replace(/[xх]/g, '×');
    var q2 = (search.value || '').trim().toLowerCase();
    var shown = 0;
    data.forEach(function (x) {
      var ok = match(x, f, '') && (!q2 || x.s.indexOf(q2) !== -1 || x.s.indexOf(q) !== -1);
      x.el.hidden = !ok;
      if (ok) shown++;
      // подсветка диаметров, подходящих под фильтр
      var good = rowsOk(x, f).map(function (r) { return r.d; });
      var filtering = f.d.length || f.a.length;
      [].forEach.call(x.el.querySelectorAll('.kr-d'), function (b) {
        b.classList.toggle('is-dim', !!filtering && !has(good, b.getAttribute('data-kr-d')));
      });
    });
    // счётчики у вариантов: сколько марок останется, если выбрать вариант
    inputs.forEach(function (el) {
      var g = el.getAttribute('data-kr-f'), v = el.getAttribute('data-kr-v');
      var on = el.type === 'checkbox' ? el.checked : el.getAttribute('aria-pressed') === 'true';
      var f2 = {};
      GROUPS.forEach(function (k) { f2[k] = k === g ? [v] : f[k]; });
      var n = data.filter(function (x) { return match(x, f2, '') && (!q2 || x.s.indexOf(q2) !== -1 || x.s.indexOf(q) !== -1); }).length;
      if (el.type === 'checkbox') {
        var lab = el.closest('.kr-f-opt');
        lab.querySelector('[data-kr-n]').textContent = n;
        lab.classList.toggle('is-off', !n && !on);
        el.disabled = !n && !on;
      } else {
        el.disabled = !n && !on;
      }
    });
    var total = 0;
    picked.textContent = '';
    GROUPS.forEach(function (g) {
      f[g].forEach(function (v) {
        total++;
        var b = document.createElement('button');
        b.type = 'button';
        b.setAttribute('data-kr-un', g);
        b.setAttribute('data-kr-v', v);
        var src = inputs.filter(function (el) { return el.getAttribute('data-kr-f') === g && el.getAttribute('data-kr-v') === v; })[0];
        var lab = src && src.closest('.kr-f-opt');
        b.textContent = g === 'd' ? v + ' мм' : (lab ? lab.querySelector('span').textContent : v);
        picked.appendChild(b);
      });
    });
    root.querySelectorAll('[data-kr-total]').forEach(function (el) { el.textContent = plural(shown); });
    var act = root.querySelector('[data-kr-active]');
    act.textContent = total ? total : '';
    root.querySelector('[data-kr-reset]').hidden = !total;
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
    inputs.forEach(function (el) {
      if (el.type === 'checkbox') el.checked = false; else el.setAttribute('aria-pressed', 'false');
    });
    search.value = '';
    apply();
  }

  function product(card) {
    var btn = card.querySelector('[data-kr-order]');
    var d = card.querySelector('.kr-d[aria-pressed="true"]');
    return btn.getAttribute('data-kc-product').split(', Ø')[0] + (d ? ', Ø ' + d.getAttribute('data-kr-d') + ' мм' : '');
  }

  function openSide(on) {
    side.classList.toggle('is-open', on);
    document.documentElement.style.overflow = on ? 'hidden' : '';
  }

  root.addEventListener('click', function (e) {
    var t = e.target;
    var chip = t.closest('.kr-f-chip');
    if (chip) { chip.setAttribute('aria-pressed', chip.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); apply(); return; }
    var un = t.closest('[data-kr-un]');
    if (un) {
      var g = un.getAttribute('data-kr-un'), v = un.getAttribute('data-kr-v');
      inputs.forEach(function (el) {
        if (el.getAttribute('data-kr-f') === g && el.getAttribute('data-kr-v') === v) {
          if (el.type === 'checkbox') el.checked = false; else el.setAttribute('aria-pressed', 'false');
        }
      });
      apply(); return;
    }
    var d = t.closest('.kr-d');
    if (d) {
      var card = d.closest('.kr-card');
      var on = d.getAttribute('aria-pressed') !== 'true';
      [].forEach.call(card.querySelectorAll('.kr-d'), function (b) { b.setAttribute('aria-pressed', 'false'); });
      d.setAttribute('aria-pressed', on ? 'true' : 'false');
      card.querySelector('[data-kr-order]').setAttribute('data-kc-product', product(card));
      return;
    }
    var ord = t.closest('[data-kr-order]');
    if (ord) {
      var pop = document.getElementById('krd-pop-order');
      if (pop) {
        var v2 = product(ord.closest('.kr-card'));
        var field = pop.querySelector('[data-kc-target]'), label = pop.querySelector('[data-kc-label]');
        if (field) field.value = v2;
        if (label) label.textContent = v2;
      }
      return;
    }
    if (t.closest('[data-kr-reset]') || t.closest('[data-kc-reset]')) { reset(); return; }
    if (t.closest('[data-kr-open]')) { openSide(true); return; }
    if (t.closest('[data-kr-close]')) { openSide(false); return; }
    if (t.closest('[data-kc-back]')) {
      if (document.referrer && document.referrer.indexOf(location.host) !== -1) history.back();
      else location.href = window.KRD_SITE_URL ? window.KRD_SITE_URL('/') : '/';
    }
  });
  root.addEventListener('change', function (e) { if (e.target.closest('[data-kr-f]')) apply(); });
  search.addEventListener('input', apply);
  sort.addEventListener('change', order);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && side.classList.contains('is-open')) openSide(false); });
  apply();
})();
'''


def main():
    cards = load()
    layout, sub = build(cards)
    s = open(DOC, encoding='utf-8').read()
    # блок со списком: между маркерами, а при первом запуске — от kc-layout до баннера
    if '<!--ropes-->' in s:
        a = s.index('<!--ropes-->'); b = s.index('<!--/ropes-->') + len('<!--/ropes-->\n')
    else:
        a = s.index('<div class="kc-layout">'); b = s.index('<section class="kc-cta">')
    s = s[:a] + layout + s[b:]
    s = re.sub(r'(<p class="kc-sub">)[^<]*(</p>)', lambda m: m.group(1) + sub + m.group(2), s, count=1)
    # стили
    if '/*ropes*/' in s:
        s = re.sub(r'\n?/\*ropes\*/.*?/\*/ropes\*/\n?', '\n', s, flags=re.S)
    i = s.index('</style>')
    s = s[:i].rstrip('\n') + '\n' + CSS.strip('\n') + '\n' + s[i:]
    # скрипт целиком
    a = s.index('<script>') + len('<script>'); b = s.index('</script>', a)
    s = s[:a] + JS + s[b:]
    open(DOC, 'w', encoding='utf-8', newline='\n').write(s)

    assert '<' not in JS, 'в скрипте не должно быть «<»'
    print('== стальные канаты: марок %d, строк %d' % (len(cards), sum(len(c['rows']) for c in cards)))
    if FIXES:
        print('Поправлено в данных при сборке:')
        for f in FIXES:
            print('  -', f)
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'tilda_block.py'), '--doc', 'steel-ropes'], check=True)
    subprocess.run(['node', os.path.join(ROOT, 'tools', 'product_page.mjs')], check=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
