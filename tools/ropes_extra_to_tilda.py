# Новые канаты от заказчика (data/ropes-gost-lifts.xlsx: листы «Лифтовые канаты», «ГОСТ 2688-80»,
# «ГОСТ 7668-80», «ГОСТ 7669-80») -> товары каталога Тильды в том же виде, что tools/ropes_to_tilda.py.
# Запуск: python tools/ropes_extra_to_tilda.py  → data/ropes-tilda-extra.json (поля для store_save_products через MCP).
#
# В листах ГОСТ свивка и прочность записаны через дробь, чтобы сократить таблицу:
# «sZ / zS» → два товара (sZ и zS), прочность «1770/1860/1960» остаётся одной характеристикой.
# Конструкция товара по ГОСТ — «6x19-FC ГОСТ 2688-80»: каталог показывает в фильтре «ГОСТ 2688-80».
# Применение приводится к названиям фильтра («башеный кран» → «Башенный кран», «экскаваторы» → «Экскаватор»,
# «гусеничныйи кран» → «Гусеничный кран», «Лифты» → «Лифт»), «иное» в фильтр не идёт.
import json, os, re, sys
from collections import OrderedDict

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ropes_page as rp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, 'data', 'ropes-gost-lifts.xlsx')
OUT = os.path.join(ROOT, 'data', 'ropes-tilda-extra.json')
AXIS = 'Диаметр, мм'
PART = '434043879043'

APP = {'лебедка': 'Лебедка', 'лебёдка': 'Лебедка', 'растяжка': 'Растяжка', 'эвакуатор': 'Эвакуатор',
       'козловой кран': 'Козловой кран', 'мостовой кран': 'Мостовой кран', 'башеный кран': 'Башенный кран',
       'башенный кран': 'Башенный кран', 'манипулятор': 'Манипулятор', 'автокран': 'Автокран',
       'буровая установка': 'Буровая установка', 'трубоукладчик': 'Трубоукладчик', 'гусеничный кран': 'Гусеничный кран', 'гусеничныйи кран': 'Гусеничный кран',
       'экскаватор': 'Экскаватор', 'экскаваторы': 'Экскаватор', 'лифт': 'Лифт', 'лифты': 'Лифт', 'иное': None}
LAY = {'sZ': ('Правая', 'Крестовая'), 'zS': ('Левая', 'Крестовая'), 'zZ': ('Правая', 'Односторонняя'),
       'sS': ('Левая', 'Односторонняя')}
CORE = {'Органический сердечник (FC)': ('FC', 'Органический (FC)'), 'Стальной': ('IWRC', 'Стальной (IWRC)'),
        'Органический (FC)': ('FC', 'Органический (FC)'), 'Органический (NF)': ('NF', 'Органический (NF)'),
        'Независимый стальной (IWRC)': ('IWRC', 'Стальной (IWRC)')}


def s(v):
    return '' if v is None else re.sub(r'\s+', ' ', str(v)).strip()


def diam(v):
    n = float(s(v).replace(',', '.'))
    return ('%g' % n).replace('.', ',')


def apps(v):
    out = []
    for a in s(v).split(','):
        a = a.strip()
        if not a:
            continue
        key = a.lower()
        if key not in APP:
            raise SystemExit('неизвестное применение: %r' % a)
        if APP[key] and APP[key] not in out:
            out.append(APP[key])
    return out


def strength(v):
    nums = re.findall(r'\d{4}', s(v))
    return ('/'.join(nums), ' / '.join(nums) + ' Н/мм²')


def rows(ws):
    data = [r for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]
    hi = next(i for i, r in enumerate(data) if s(r[0]) == 'Диаметр, мм')
    head = [s(h) for h in data[hi]]
    col = lambda name, nth=0: [i for i, h in enumerate(head) if h == name][nth]  # noqa: E731
    adv = [i for i, h in enumerate(head) if h.startswith('Преимущество')]
    for r in data[hi + 1:]:
        if not s(r[0]):
            continue
        yield dict(d=diam(r[0]), constr=s(r[col('Конструкция', 2)]).replace('х', 'x').replace('X', 'x'),
                   gost=s(r[col('Конструкция', 1)]) if ws.title.startswith('ГОСТ') else '',
                   coat=s(r[col('Тип покрытия')]), apps=apps(r[col('Применение')]),
                   strands=s(r[col('Количество прядей')]), core=s(r[col('Сердечник')]),
                   lays=[x.strip() for x in s(r[col('Обозначение свивки')]).split('/')],
                   nonrot=s(r[col('Некрутящийся канат')]), strength=strength(r[col('Временное сопротивление разрыву проволоки')]),
                   desc=s(r[col('Описание канатов')]), adv=[s(r[i]) for i in adv if s(r[i])],
                   cert=s(r[col('Сертификаты')]))


def products():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    marks = OrderedDict()
    for ws in wb:
        for r in rows(ws):
            short, core = CORE[r['core']]
            base = r['constr'] if r['constr'].endswith('-' + short) else '%s-%s' % (r['constr'], short)
            coat = r['coat'].split()[0]
            for lay in r['lays']:
                code = '%s-%s-%s-%s' % (base, lay, coat, r['strength'][0])
                m = marks.setdefault(code, dict(r, base=base, core_full=core, lay=lay, code=code, rows=[], descs=[]))
                m['rows'].append((r['d'], r['apps']))
                m['descs'].append(r['desc'])
    items = []
    for m in marks.values():
        rows_ = sorted(OrderedDict(m['rows']).items(), key=lambda x: float(x[0].replace(',', '.')))
        order = rp.present(rp.APP_ORDER, {a for _, aa in rows_ for a in aa})
        groups = OrderedDict()
        for d, aa in rows_:
            groups.setdefault(', '.join(a for a in order if a in aa) or '—', []).append(d)
        constr = m['base'] + (' ГОСТ ' + m['gost'] if m['gost'] else '')
        chars = [('Марка', m['code']), ('Конструкция', constr), ('Количество прядей', m['strands']),
                 ('Сердечник', m['core_full']), ('Направление свивки', LAY[m['lay']][0]), ('Тип свивки', LAY[m['lay']][1]),
                 ('Обозначение свивки', m['lay']), ('Тип покрытия', m['coat']),
                 ('Покрытие проволоки', 'Оцинкованная' if m['coat'].startswith('Galv') else 'Неоцинкованная'),
                 ('Некрутящийся канат', m['nonrot']), ('Временное сопротивление разрыву', m['strength'][1])]
        if len(groups) == 1:
            chars.append(('Применение', next(iter(groups))))
        else:
            # Тильда режет названия характеристик до 40 символов: длинный список диаметров — на несколько строк
            for a, ds in groups.items():
                part = []
                for d in ds:
                    if part and len('Применение, Ø %s мм' % '; '.join(part + [d])) > 40:
                        chars.append(('Применение, Ø %s мм' % '; '.join(part), a))
                        part = []
                    part.append(d)
                chars.append(('Применение, Ø %s мм' % '; '.join(part), a))
        chars.append(('Сертификаты', m['cert']))
        for t, _ in chars:
            assert len(t) <= 40, t
        desc = max(set(m['descs']), key=m['descs'].count)
        title = 'Канат ' + (m['constr'] + ' ГОСТ ' + m['gost'] if m['gost'] else m['base'])
        items.append(dict(
            title=title, sku=m['code'], descr=desc,
            text=''.join(__import__('ropes_to_tilda').adv_p(a) for a in m['adv']),
            characteristics=dict(title=[t for t, _ in chars], value=[str(v) for _, v in chars]),
            editions={'uid': [''] * len(rows_),
                      'sku': ['%s-%s' % (m['code'], d.replace(',', '.')) for d, _ in rows_],
                      'price': ['0'] * len(rows_), AXIS: [d for d, _ in rows_]},
            partuids=PART))
    return items


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    items = products()
    old = {}
    if os.path.exists(OUT):  # uid уже созданных товаров сохраняем
        old = {i['sku']: i.get('productuid') for i in json.load(open(OUT, encoding='utf-8'))}
    for it in items:
        if old.get(it['sku']):
            it['productuid'] = old[it['sku']]
    json.dump(items, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('товаров: %d, вариантов: %d -> %s' % (len(items), sum(len(i['editions']['sku']) for i in items), os.path.relpath(OUT, ROOT)))
    for it in items:
        ch = dict(zip(it['characteristics']['title'], it['characteristics']['value']))
        ap = [v for t, v in ch.items() if t.startswith('Применение')]
        print('%s | %s | %d диам. %s–%s | применение: %d групп(ы), %s' % (
            it['title'], it['sku'], len(it['editions']['sku']), it['editions'][AXIS][0], it['editions'][AXIS][-1],
            len(ap), ' + '.join(sorted({a for v in ap for a in v.split(', ')}))))


if __name__ == '__main__':
    main()
