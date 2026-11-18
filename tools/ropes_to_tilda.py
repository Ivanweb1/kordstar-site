# Стальные канаты из data/steel-ropes.xlsx -> товары каталога Тильды (Магазин → Товары).
# Одна марка (полный код) = один товар, диаметры = варианты «Диаметр, мм», параметры = характеристики.
# Запуск: python tools/ropes_to_tilda.py  → data/ropes-tilda.json (поля для store_save_products через MCP).
# Применение у разных диаметров бывает разным: если одинаковое — одна характеристика «Применение»,
# если у диаметров списки разные — по строке на группу: «Применение, Ø 8; 9; 10 мм» (их читают каталог и карточка).
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ropes_page as rp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'ropes-tilda.json')
AXIS = 'Диаметр, мм'


def adv_p(a):
    m = re.match(r'([^.]+\.)\s*(.*)', a)
    esc = rp.esc
    return '<p><b>%s</b> %s</p>' % (esc(m.group(1)), esc(m.group(2))) if m else '<p>%s</p>' % esc(a)


def product(c):
    apps_all = [a for a in rp.present(rp.APP_ORDER, {a for r in c['rows'] for a in r['apps']})]
    groups = {}
    for r in c['rows']:
        groups.setdefault(', '.join(a for a in apps_all if a in r['apps']) or '—', []).append(r['label'])
    chars = [('Марка', c['code']), ('Конструкция', c['constr']), ('Количество прядей', c['strands']),
             ('Сердечник', c['core']), ('Направление свивки', c['dir']), ('Тип свивки', c['kind']),
             ('Обозначение свивки', c['lay']), ('Тип покрытия', c['fcoat']), ('Покрытие проволоки', c['coating']),
             ('Некрутящийся канат', c['nonrot']), ('Временное сопротивление разрыву', c['strength'])]
    if len(groups) == 1:
        chars.append(('Применение', next(iter(groups))))
    else:  # разное применение у диаметров: «Применение, Ø 8; 9; 10 мм»
        for apps, ds in groups.items():
            chars.append(('Применение, Ø %s мм' % '; '.join(ds), apps))
    chars.append(('Сертификаты', c['cert']))
    for t, _ in chars:
        assert len(t) <= 40, t
    return dict(
        title='Канат ' + c['constr'],
        sku=c['code'],
        descr=c['desc'],
        text=''.join(adv_p(a) for a in c['adv']),
        characteristics=dict(title=[t for t, _ in chars], value=[str(v) for _, v in chars]),
        editions={'uid': [''] * len(c['rows']),
                  'sku': ['%s-%s' % (c['code'], r['label'].replace(',', '.')) for r in c['rows']],
                  'price': ['0'] * len(c['rows']),
                  AXIS: [r['label'] for r in c['rows']]},
    )


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    cards = rp.load()
    items = [product(c) for c in cards]
    json.dump(items, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('товаров: %d, вариантов: %d -> %s' % (len(items), sum(len(i['editions']['sku']) for i in items), os.path.relpath(OUT, ROOT)))
    for i, it in enumerate(items):
        extra = [t for t in it['characteristics']['title'] if t.startswith('Применение, ')]
        print('%2d %s | %s | %d диам.%s' % (i, it['title'], it['sku'], len(it['editions']['sku']), (' | ' + ', '.join(extra)) if extra else ''))


if __name__ == '__main__':
    main()
