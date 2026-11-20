# -*- coding: utf-8 -*-
"""Страница «Каталог» (/catalog) — общий раздел со всеми категориями (прототип: design/kordstar-prototypes.fig,
раздел «Каталог», фрейм «Каталог»).

Запуск:  python tools/catalog_page.py
Пишет середину страницы в tilda/_doc_catalog.html и собирает через tools/tilda_block.py --doc catalog
вайб-блок tilda/catalog.html (+ превью tilda/catalog-preview.html) — с шапкой, подвалом и поп-апами главной.

Пока без фото: вместо снимка товара — плашка с иконкой категории с главной.
Список товаров — CATS ниже; поменяли — перезапустить скрипт и перевставить блок в Тильде.
"""
import html
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tilda')

PRICE = 'Цена по запросу'

# (id, название, иконка с главной, подпись, [(товар, пояснение)], заявка вместо товаров)
CATS = [
    ('ropes', 'Стальные канаты', 'img/Frame_2136139848-32303965.webp',
     'Канаты для подъёмной, строительной и буровой техники. Диаметр от 3 до 100 мм.', [
         ('Канаты для башенных кранов', 'Подберём конструкцию и диаметр под модель крана и высоту подъёма.'),
         ('Канаты для автокранов', 'Для грузовой и стреловой лебёдки, оцинкованные и без покрытия.'),
         ('Канаты для буровых установок', 'Талевые и вспомогательные канаты для буровой техники.'),
         ('Канаты ГОСТ 2688-80', 'Двойной свивки, Galv и Ung, любое направление свивки.'),
         ('Канаты ГОСТ 7668-80', 'Двойной свивки, повышенная гибкость, Galv и Ung.'),
         ('Канаты ГОСТ 7669-80', 'Двойной свивки с металлическим сердечником, Galv и Ung.'),
     ], None),
    ('slings', 'Стропы', 'img/Frame_2136139854-64383361.webp',
     'Текстильные, цепные и канатные стропы грузоподъёмностью до 90 т.', [
         ('Текстильные петлевые и кольцевые стропы', 'СТП и СТК, грузоподъёмность от 1 до 32 т.'),
         ('Текстильные ветвевые стропы', '1СТ, 3СТ, 4СТ — от одной до четырёх ветвей.'),
         ('Текстильные круглопрядные стропы', 'СТКК и СТПК — бережно к поверхности груза.'),
         ('Буксировочные тросы текстильные', 'БТДк — для буксировки автотранспорта.'),
         ('ВММП стропы', 'Высокопрочные монтажные полотенца для тяжёлых грузов.'),
         ('Цепные ветвевые стропы', '2СЦ, 3СЦ, 4СЦ, ВЦ — грузоподъёмность до 40 т.'),
         ('Цепные кольцевые стропы', 'УСЦ2 — для длинномерных и крупных грузов.'),
         ('Ветвь канатная', 'ВК — основа для канатных строп под задачу.'),
         ('Канатные ветвевые стропы', '1СК, 2СК, 3СК, 4СК — грузоподъёмность до 90 т.'),
         ('Канатные кольцевые стропы', 'УСК2 и СКК — для обвязки груза.'),
         ('Канатные петлевые стропы', 'УСК1 и СКП — универсальные стропы с петлями.'),
         ('Буксировочные тросы канатные', 'БТК — стальные тросы для буксировки.'),
     ], None),
    ('parts-slings', 'Комплектующие для строп', 'img/Frame_2136139853-65656336.webp',
     'Всё, чтобы собрать или отремонтировать стропу и закрепить груз.', [
         ('Цепи', 'Цепи классов Т8 и Т10 для цепных строп.'),
         ('Крюки цепные', 'С проушиной и защёлкой, самозакрывающиеся, укорачивающие, с вертлюгом.'),
         ('Звенья соединительные для цепей', 'Для сборки цепных строп, от 0,8 до 40 т.'),
         ('Крюки для канатных строп', 'Крюки под канатные стропы разной грузоподъёмности.'),
         ('Втулки алюминиевые', 'Для опрессовки петель канатных строп.'),
         ('Звенья соединительные для канатных строп', 'Для подвески канатных ветвей.'),
         ('Коуши DIN 6899', 'Защищают петлю каната от износа и заломов.'),
         ('Стяжные ремни', 'Для крепления грузов при перевозке, от 0,4 до 20 т.'),
         ('Талрепы', 'Вилка-вилка DIN 1478 и другие исполнения.'),
         ('Крепёжные цепи', 'Для крепления тяжёлых грузов на платформе.'),
     ], None),
    ('rigging', 'Такелажные изделия', 'img/Frame_2136139862-34373065.webp',
     'Зажимы, скобы, рым-болты, втулки и коуши для канатных систем.', [
         ('Зажимы канатные', 'DIN 1142 и DIN 741, для каната от 5 до 40 мм.'),
         ('Скобы', 'Прямые и омегообразные, от 0,08 до 55 т.'),
         ('Рым-болты', 'Прикручиваемые и поворотные, резьба от М6 до М100.'),
         ('Втулка алюминиевая', 'Для каната от 8 до 40 мм.'),
         ('Коуш DIN 6899', 'Для каната от 8 до 40 мм.'),
         ('Коуш DIN 3091', 'Усиленный, для каната от 12 до 40 мм.'),
     ], None),
    ('spare', 'Запасные части', 'img/Frame_2136139863-66633832.webp',
     'Запчасти для строительной и специальной техники — подберём по артикулу или названию детали.', [],
     ('Подбор запасных частей', 'Укажите производителя, деталь и артикул — свяжемся в течение 30 минут.')),
    ('drill', 'Буровой инструмент и оснастка', 'img/Frame_2136139864-38343833.webp',
     'Инструмент и комплектующие для буровой техники — подберём по артикулу или названию.', [],
     ('Подбор бурового инструмента', 'Укажите производителя, деталь и артикул — свяжемся в течение 30 минут.')),
]

HOW_TO = [
    ('Назначение', 'Определите, для чего нужен канат: подъём, буксировка, растяжка, ограждение и т.д.'),
    ('Материал', 'Стальной — для высокой нагрузки и прочности. Синтетический — легче, устойчив к влаге и коррозии.'),
    ('Диаметр', 'Количество прядей и тип свивки влияют на гибкость и износостойкость.'),
    ('Покрытие', 'Оцинковка или ПВХ-защита — для работы на улице и во влажной среде.'),
    ('Соответствие DIN', 'Убедитесь, что канат соответствует нужному DIN-стандарту (например, DIN 3055, DIN 3060 и др.).'),
]
WHERE = [
    ('Строительство', 'подъём и перемещение грузов'),
    ('Промышленность', 'оборудование, краны, лебёдки'),
    ('Судоходство', 'швартовка, такелаж'),
    ('Авто и транспорт', 'буксировка, крепление грузов'),
    ('Инфраструктура', 'мосты, ограждения, тросовые системы'),
    ('Быт и туризм', 'палатки, страховка, хозяйственные задачи'),
]

E = html.escape

# Разделы, которые пока не работают: в боковом меню и чипсах — серые и некликабельные,
# в списке справа — только заголовок раздела, без товаров.
INACTIVE = {'slings', 'parts-slings', 'rigging', 'spare', 'drill'}


def count(c):
    return len(c[4]) if c[4] else 1


def total():
    return sum(count(c) for c in CATS if c[0] not in INACTIVE)


def card(cat, title, text, button, popup, rank):
    cid, cname, icon = cat[0], cat[1], cat[2]
    detail = (''  # карточка /strop-1sk теперь про канат 6x19W-IWRC, ссылку со стропов убрали
              if title == 'Канатные ветвевые стропы' else '')
    return (
        '<article class="kc-card%s" data-kc-cat="%s" data-kc-name="%s" data-kc-rank="%d">'
        '<div class="kc-card__ph"><img src="%s" alt="" width="72" height="72" loading="lazy"></div>'
        '<h3 class="kc-card__title">%s</h3>'
        '<p class="kc-card__text">%s</p>'
        '%s'
        '<p class="kc-card__price">%s</p>'
        '<button class="kc-card__btn" type="button" data-krd-popup="%s" data-kc-product="%s">%s</button>'
        '</article>'
    ) % ('' if popup == 'order' else ' kc-card--wide', cid, E(title.lower()), rank, icon, E(title), E(text), detail,
         PRICE if popup == 'order' else 'Ответ за 30 минут', popup, E(title if popup == 'order' else cname), button)


def groups():
    out = []
    for c in CATS:
        cid, cname, icon, lead, items, req = c
        if cid in INACTIVE:
            out.append(
                '<section class="kc-group kc-group--off" data-kc-group="%s" data-kc-off>'
                '<div class="kc-group__head"><h2 class="kc-group__title">%s</h2></div></section>' % (cid, E(cname)))
            continue
        if items:
            cards = ''.join(card(c, t, d, 'Предзаказ', 'order', i) for i, (t, d) in enumerate(items))
        else:
            cards = card(c, req[0], req[1], 'Оставить запрос', 'parts', 0)
        heading = '<a href="/steel-ropes">Стальные канаты</a>' if cid == 'ropes' else E(cname)
        out.append(
            '<section class="kc-group" data-kc-group="%s">'
            '<div class="kc-group__head"><div><h2 class="kc-group__title">%s <span class="kc-group__count">%d</span></h2>'
            '<p class="kc-group__lead">%s</p></div></div>'
            '<div class="kc-grid">%s</div></section>' % (cid, heading, count(c), E(lead), cards))
    return '\n'.join(out)


def chips():
    out = ['<button class="kc-chip is-active" type="button" data-kc-show="all" aria-pressed="true">Все <span>%d</span></button>' % total()]
    for c in CATS:
        if c[0] in INACTIVE:
            out.append('<button class="kc-chip" type="button" disabled>%s</button>' % E(c[1]))
        else:
            out.append('<button class="kc-chip" type="button" data-kc-show="%s" aria-pressed="false">%s <span>%d</span></button>'
                       % (c[0], E(c[1]), count(c)))
    return ''.join(out)


def side():
    out = ['<li><button type="button" class="is-active" data-kc-show="all">Все товары<span>%d</span></button></li>' % total()]
    for c in CATS:
        if c[0] in INACTIVE:
            out.append('<li><button type="button" disabled>%s</button></li>' % E(c[1]))
        else:
            out.append('<li><button type="button" data-kc-show="%s">%s<span>%d</span></button></li>' % (c[0], E(c[1]), count(c)))
    return ''.join(out)


def info_pop(pid, kicker, title, lead, rows):
    items = ''.join('<li><b>%s</b><span>%s</span></li>' % (E(a), E(b)) for a, b in rows)
    return (
        '<div class="krd-pop" id="krd-pop-%s" role="dialog" aria-modal="true" aria-labelledby="krd-pop-%s-t">'
        '<div class="krd-pop__overlay" data-krd-close></div><div class="krd-pop__box">'
        '<button class="krd-pop__close" type="button" aria-label="Закрыть" data-krd-close></button>'
        '<div class="krd-pop__body"><p class="krd-pop__kicker">%s</p>'
        '<h3 class="krd-pop__title" id="krd-pop-%s-t">%s</h3><p class="krd-pop__lead">%s</p>'
        '<ul class="kc-info">%s</ul>'
        '<button class="krd-btn" type="button" data-krd-popup="pick">Получить консультацию</button>'
        '</div></div></div>'
    ) % (pid, pid, kicker, pid, title, lead, items)


AGREE = ('<label class="krd-agree"><input type="checkbox" name="agree" required data-krd-skip><span class="krd-agree__box"></span>'
         '<span class="krd-agree__text">Даю <a href="/soglasie" data-krd-link="consent">согласие на обработку персональных данных</a> '
         'и соглашаюсь с <a href="/policy" data-krd-link="policy">политикой конфиденциальности</a></span></label>')
CONTACT = ('<div class="krd-form__row">'
           '<label class="krd-field"><span class="krd-field__label">Имя <i>— необязательно</i></span>'
           '<input name="name" type="text" autocomplete="name" placeholder="Как к вам обращаться"></label>'
           '<label class="krd-field"><span class="krd-field__label">Телефон</span>'
           '<input name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></label></div>')


def form_pop(pid, kicker, title, lead, form_name, fields, done):
    return (
        '<div class="krd-pop" id="krd-pop-%s" role="dialog" aria-modal="true" aria-labelledby="krd-pop-%s-t">'
        '<div class="krd-pop__overlay" data-krd-close></div><div class="krd-pop__box">'
        '<button class="krd-pop__close" type="button" aria-label="Закрыть" data-krd-close></button>'
        '<div class="krd-pop__body"><p class="krd-pop__kicker">%s</p>'
        '<h3 class="krd-pop__title" id="krd-pop-%s-t">%s</h3><p class="krd-pop__lead">%s</p>'
        '<form class="krd-form t-form-off" data-krd-form="%s" novalidate>%s%s%s'
        '<button class="krd-btn" type="submit">Отправить заявку</button></form></div>'
        '<div class="krd-pop__done"><span class="krd-pop__check"></span><h3 class="krd-pop__title">Заявка отправлена</h3>'
        '<p class="krd-pop__lead">%s</p><button class="krd-btn krd-btn--ghost" type="button" data-krd-close>Закрыть</button></div>'
        '</div></div>'
    ) % (pid, pid, kicker, pid, title, lead, form_name, fields, CONTACT, AGREE, done)


ORDER_FIELDS = (
    '<p class="kc-pick"><span>Товар</span><b data-kc-label></b></p>'
    '<input name="product" type="hidden" data-label="Товар" data-kc-target>'
    '<div class="krd-form__row">'
    '<label class="krd-field"><span class="krd-field__label">Количество <i>— необязательно</i></span>'
    '<input name="qty" type="text" data-label="Количество" placeholder="200 м или 10 шт"></label>'
    '<label class="krd-field"><span class="krd-field__label">Параметры <i>— необязательно</i></span>'
    '<input name="params" type="text" data-label="Параметры" placeholder="Диаметр, длина"></label></div>'
)
PARTS_FIELDS = (
    '<p class="kc-pick"><span>Раздел</span><b data-kc-label></b></p>'
    '<input name="section" type="hidden" data-label="Раздел" data-kc-target>'
    '<div class="krd-form__row">'
    '<label class="krd-field"><span class="krd-field__label">Производитель</span>'
    '<input name="maker" type="text" data-label="Производитель" placeholder="Производитель техники"></label>'
    '<label class="krd-field"><span class="krd-field__label">Артикул <i>— если есть</i></span>'
    '<input name="sku" type="text" data-label="Артикул" placeholder="Артикул детали"></label></div>'
    '<label class="krd-field"><span class="krd-field__label">Наименование детали</span>'
    '<input name="part" type="text" data-label="Деталь" placeholder="Что нужно подобрать"></label>'
)

POPS = '\n'.join([
    form_pop('order', 'Предзаказ', 'Оформить предзаказ',
             'Уточним наличие, сроки и цену и перезвоним вам.', 'Предзаказ из каталога', ORDER_FIELDS,
             'Менеджер свяжется с вами, уточнит параметры и пришлёт расчёт.'),
    form_pop('parts', 'Подбор по артикулу', 'Подобрать деталь',
             'Мы свяжемся с вами в течение 30 минут.', 'Запрос запчасти из каталога', PARTS_FIELDS,
             'Инженер свяжется с вами в течение 30 минут.'),
    info_pop('howto', 'Подсказка', 'Как выбрать канат?', 'На что смотреть при выборе — по порядку.', HOW_TO),
    info_pop('where', 'Подсказка', 'Где применяется?', 'Канаты, стропы и такелаж работают почти в любой отрасли.', WHERE),
])

CSS = """
.vb-krd .vb-krd-cat{--kc-ink:#203133;--kc-head:#204043;--kc-muted:#5f7375;--kc-accent:#457c82;--kc-accent-2:#69979c;--kc-line:#dce7e8;--kc-soft:#eef5f6;
display:block;background:linear-gradient(180deg,#f4f8f9 0%,#eaf3f3 55%,#f4f8f9 100%);color:var(--kc-ink);font-family:"Inter","Montserrat",Arial,sans-serif;-webkit-font-smoothing:antialiased}
.vb-krd .vb-krd-cat *,.vb-krd .vb-krd-cat *::before,.vb-krd .vb-krd-cat *::after{box-sizing:border-box}
.vb-krd .vb-krd-cat button{font-family:inherit}
.vb-krd .kc-wrap{max-width:1200px;margin:0 auto;padding:104px 100px 0}
.vb-krd .kc-crumbs{display:flex;flex-wrap:wrap;align-items:center;row-gap:8px;margin:0 0 28px;font-size:13px;line-height:1.2;color:#7a8c8e}
.vb-krd .kc-crumbs a{color:#7a8c8e;text-decoration:none;transition:color .2s}
.vb-krd .kc-crumbs a:hover{color:var(--kc-accent)}
.vb-krd .kc-crumbs button{display:inline-flex;align-items:center;gap:8px;height:30px;margin:0 16px 0 0;padding:0 14px 0 12px;border:1px solid #d6e3e4;border-radius:30px;background:#fff;color:var(--kc-accent);font:inherit;font-weight:500;cursor:pointer;transition:border-color .2s}
.vb-krd .kc-crumbs button::before{content:"";width:6px;height:6px;border-left:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(45deg)}
.vb-krd .kc-crumbs button:hover{border-color:var(--kc-accent)}
.vb-krd .kc-crumbs button+i{display:none}
.vb-krd .kc-crumbs i{margin:0 8px;font-style:normal;color:#c3d1d2}
.vb-krd .kc-crumbs span{color:#203133;font-weight:500}
.vb-krd .kc-top{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;margin:0 0 32px}
.vb-krd .kc-sub{margin:12px 0 0;font-size:15px;line-height:1.4;color:rgba(32,49,51,.75)}
.vb-krd .kc-title{margin:0;font-family:"Montserrat",Arial,sans-serif;font-size:34px;line-height:1;font-weight:700;text-transform:uppercase;color:var(--kc-head)}
.vb-krd .kc-help{display:flex;gap:8px;flex-wrap:wrap}
.vb-krd .kc-help button{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 18px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;color:var(--kc-ink);font-size:14px;font-weight:500;cursor:pointer;transition:border-color .2s,color .2s}
.vb-krd .kc-help button::before{content:"?";display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:50%;background:var(--kc-soft);color:var(--kc-accent);font-size:12px;font-weight:700}
.vb-krd .kc-help button:hover{border-color:var(--kc-accent-2);color:var(--kc-accent)}
.vb-krd .kc-chips{display:none;gap:8px;margin:0 0 16px}
.vb-krd .kc-chip{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 16px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;color:var(--kc-ink);font-size:14px;font-weight:500;cursor:pointer;transition:background-color .2s,border-color .2s,color .2s}
.vb-krd .kc-chip span{font-size:12px;color:var(--kc-muted)}
.vb-krd .kc-chip:hover{border-color:var(--kc-accent-2)}
.vb-krd .kc-chip.is-active{background:var(--kc-accent);border-color:var(--kc-accent);color:#fff}
.vb-krd .kc-chip.is-active span{color:rgba(255,255,255,.75)}
.vb-krd .kc-tools{display:flex;gap:12px;margin:0 0 32px}
.vb-krd .kc-search{position:relative;flex:1;min-width:0}
.vb-krd .kc-search input{width:100%;height:44px;padding:0 44px 0 20px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;font:inherit;font-size:14px;color:var(--kc-ink);outline:none;transition:border-color .2s}
.vb-krd .kc-search input:focus{border-color:var(--kc-accent-2)}
.vb-krd .kc-search svg{position:absolute;right:16px;top:12px;width:20px;height:20px;pointer-events:none}
.vb-krd .kc-sort{position:relative}
.vb-krd .kc-sort select{height:44px;padding:0 44px 0 20px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;font:inherit;font-size:14px;color:var(--kc-ink);cursor:pointer;outline:none;-webkit-appearance:none;appearance:none}
.vb-krd .kc-sort select:focus{border-color:var(--kc-accent-2)}
.vb-krd .kc-sort::after{content:"";position:absolute;right:20px;top:17px;width:7px;height:7px;border-right:2px solid var(--kc-accent);border-bottom:2px solid var(--kc-accent);transform:rotate(45deg);pointer-events:none}
.vb-krd .kc-layout{display:grid;grid-template-columns:232px minmax(0,1fr);gap:20px;align-items:start}
.vb-krd .kc-list{min-width:0}
.vb-krd .kc-side{position:sticky;top:96px;background:#fff;border-radius:24px;padding:20px 16px;box-shadow:0 10px 30px rgba(32,64,67,.05)}
.vb-krd .kc-side__title{margin:0 0 14px;font-family:"Montserrat",Arial,sans-serif;font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--kc-head)}
.vb-krd .kc-side ul{list-style:none;margin:0;padding:0}
.vb-krd .kc-side li+li{margin-top:2px}
.vb-krd .kc-side li button span{flex:none;font-size:12px;color:var(--kc-muted)}
.vb-krd .kc-side li button.is-active span{color:var(--kc-accent-2)}
.vb-krd .kc-side li button{display:flex;justify-content:space-between;align-items:baseline;gap:12px;width:100%;padding:9px 12px;border:0;border-radius:12px;background:none;text-align:left;font-size:14px;line-height:1.35;color:var(--kc-ink);cursor:pointer;transition:background-color .2s,color .2s}
.vb-krd .kc-side li button:hover{background:var(--kc-soft)}
.vb-krd .kc-side li button.is-active{background:var(--kc-soft);color:var(--kc-accent);font-weight:600}
.vb-krd .kc-side li button:disabled{color:#a9b8b9;cursor:default;background:none}
.vb-krd .kc-chip:disabled{color:#a9b8b9;cursor:default;border-color:var(--kc-line)}
.vb-krd .kc-group+.kc-group{margin-top:48px}
.vb-krd .kc-group--off+.kc-group--off{margin-top:20px}
.vb-krd .kc-group--off .kc-group__head{margin:0}
.vb-krd .kc-group--off .kc-group__title{margin:0}
.vb-krd .kc-group[hidden],.vb-krd .kc-card[hidden]{display:none}
.vb-krd .kc-group__head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin:0 0 20px}
.vb-krd .kc-group__title{margin:0 0 6px;font-family:"Montserrat",Arial,sans-serif;font-size:22px;line-height:1.2;font-weight:700;color:var(--kc-head)}
.vb-krd .kc-group__title a{color:inherit;text-decoration:none}
.vb-krd .kc-group__title a:hover{color:var(--kc-accent)}
.vb-krd .kc-group__count{display:inline-block;vertical-align:middle;margin-left:6px;padding:3px 10px;border-radius:20px;background:#fff;font-family:"Inter",Arial,sans-serif;font-size:12px;font-weight:500;color:var(--kc-muted)}
.vb-krd .kc-group__lead{margin:0;font-size:14px;line-height:1.4;color:rgba(32,49,51,.8)}
.vb-krd .kc-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.vb-krd .kc-card{display:flex;flex-direction:column;background:#fff;border-radius:20px;padding:8px 8px 12px;box-shadow:0 10px 30px rgba(32,64,67,.05);transition:box-shadow .25s,transform .25s}
.vb-krd .kc-card:hover{box-shadow:0 18px 40px rgba(32,64,67,.12);transform:translateY(-2px)}
.vb-krd .kc-card__ph{display:flex;align-items:center;justify-content:center;aspect-ratio:4/3;margin:0 0 12px;border-radius:14px;background:radial-gradient(120% 100% at 50% 0%,#f3f9f9 0%,#e3eff0 100%)}
.vb-krd .kc-card__ph img{width:60px;height:60px;border-radius:16px;background:#fff;box-shadow:0 10px 26px rgba(32,64,67,.12)}
.vb-krd .kc-card--wide{grid-column:1/-1;display:grid;grid-template-columns:200px 1fr auto;grid-template-rows:auto auto 1fr;column-gap:28px;align-items:start;padding:12px 32px 12px 12px}
.vb-krd .kc-card--wide .kc-card__ph{grid-row:1/4;aspect-ratio:auto;height:100%;min-height:130px;margin:0}
.vb-krd .kc-card--wide .kc-card__title{grid-column:2;margin-top:20px;font-size:17px}
.vb-krd .kc-card--wide .kc-card__text{grid-column:2;max-width:520px}
.vb-krd .kc-card--wide .kc-card__price{grid-column:2;margin-top:0;margin-bottom:20px}
.vb-krd .kc-card--wide .kc-card__btn{grid-column:3;grid-row:1/4;align-self:center;padding:0 32px;background:var(--kc-accent);border-color:var(--kc-accent);color:#fff}
.vb-krd .kc-card--wide .kc-card__btn:hover{background:#3a6a6f;border-color:#3a6a6f}
.vb-krd .kc-card__title{margin:0 4px 6px;font-family:"Inter",Arial,sans-serif;font-size:14px;line-height:1.35;font-weight:600;color:var(--kc-ink)}
.vb-krd .kc-card__detail{margin:0 4px 8px;color:#204043;font-size:13px;font-weight:700;text-decoration:underline;text-underline-offset:3px}
.vb-krd .kc-card__text{margin:0 4px 10px;font-size:12px;line-height:1.4;color:rgba(32,49,51,.8)}
.vb-krd .kc-card__price{margin:auto 4px 10px;font-size:13px;font-weight:600;color:var(--kc-head)}
.vb-krd .kc-card__btn{height:38px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;color:var(--kc-ink);font-size:13px;font-weight:500;cursor:pointer;transition:background-color .2s,border-color .2s,color .2s}
.vb-krd .kc-card__btn:hover{background:var(--kc-accent);border-color:var(--kc-accent);color:#fff}
.vb-krd .kc-empty{display:none;padding:56px 24px;border-radius:24px;background:#fff;text-align:center}
.vb-krd .kc-empty.is-shown{display:block}
.vb-krd .kc-empty p{margin:0 0 20px;font-size:16px;color:var(--kc-muted)}
.vb-krd .kc-empty button{height:44px;padding:0 22px;border:1px solid var(--kc-line);border-radius:30px;background:#fff;font-size:14px;color:var(--kc-ink);cursor:pointer}
.vb-krd .kc-cta{margin:72px 0 0;padding:0 0 88px}
.vb-krd .kc-cta__box{display:flex;flex-direction:column;align-items:flex-start;justify-content:center;min-height:192px;padding:36px 48px;border-radius:40px;background:#24393b url(img/Content2_1-32346136.webp) right center/cover no-repeat;color:#fff}
.vb-krd .kc-cta h2{margin:0 0 12px;font-family:"Inter",Arial,sans-serif;font-size:20px;line-height:1.2;font-weight:600;color:#fff}
.vb-krd .kc-cta p{max-width:560px;margin:0 0 24px;font-size:14px;line-height:1.5;color:#fff}
.vb-krd .kc-cta button{display:inline-flex;align-items:center;gap:14px;height:48px;padding:0 24px 0 32px;border:0;border-radius:30px;background:#437d83;color:#f4f8f9;font-size:12px;font-weight:500;cursor:pointer;transition:background-color .2s}
.vb-krd .kc-cta button svg{width:18px;height:18px}
.vb-krd .kc-cta button:hover{background:#3a6a6f}
.vb-krd .kc-info{list-style:none;margin:0 0 24px;padding:0;display:grid;gap:10px}
.vb-krd .kc-info li{display:grid;gap:4px;padding:14px 16px;border-radius:14px;background:#f4f8f9;font-size:14px;line-height:1.45;color:#203133}
.vb-krd .kc-info b{font-weight:600;color:#457c82}
.vb-krd .kc-pick{display:flex;flex-direction:column;gap:4px;margin:0;padding:14px 18px;border-radius:14px;background:#eef5f6}
.vb-krd .kc-pick span{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#69979c}
.vb-krd .kc-pick b{font-size:16px;font-weight:600;line-height:1.35;color:#203133}
@media (max-width:959px){
.vb-krd .kc-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.vb-krd .kc-wrap{padding:100px 20px 0}
.vb-krd .kc-layout{grid-template-columns:minmax(0,1fr)}
.vb-krd .kc-side{display:none}
.vb-krd .kc-top{flex-direction:column;align-items:flex-start;gap:16px}
.vb-krd .kc-chips{display:flex;flex-wrap:nowrap;overflow-x:auto;margin:0 -20px 16px;padding:0 20px 4px;scrollbar-width:none}
.vb-krd .kc-chips::-webkit-scrollbar{display:none}
.vb-krd .kc-chip{flex:none}
.vb-krd .kc-tools{margin-bottom:28px}
}
@media (max-width:639px){
.vb-krd .kc-wrap{padding:88px 20px 0}
.vb-krd .kc-chips{margin:0 -20px 16px;padding:0 20px 4px}
.vb-krd .kc-title{font-size:26px}
.vb-krd .kc-help{gap:6px}
.vb-krd .kc-help button{height:36px;padding:0 12px;font-size:13px;gap:6px}
.vb-krd .kc-help button::before{width:16px;height:16px;font-size:11px}
.vb-krd .kc-tools{flex-direction:column}
.vb-krd .kc-sort select{width:100%}
.vb-krd .kc-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.vb-krd .kc-group+.kc-group{margin-top:40px}
.vb-krd .kc-group__head{flex-direction:column;align-items:flex-start;gap:12px}
.vb-krd .kc-group__title{font-size:19px}
.vb-krd .kc-card{border-radius:20px;padding:8px 8px 12px}
.vb-krd .kc-card__ph{margin-bottom:12px;border-radius:14px}
.vb-krd .kc-card__ph img{width:64px;height:64px;border-radius:16px}
.vb-krd .kc-card--wide{display:flex;align-items:stretch;padding:8px 8px 12px}
.vb-krd .kc-card--wide .kc-card__ph{aspect-ratio:auto;min-height:120px;height:auto;margin-bottom:12px}
.vb-krd .kc-card--wide .kc-card__title{margin-top:0}
.vb-krd .kc-card--wide .kc-card__title{font-size:16px}
.vb-krd .kc-card--wide .kc-card__price{margin-bottom:14px}
.vb-krd .kc-card--wide .kc-card__btn{padding:0;align-self:stretch}
.vb-krd .kc-card__title{font-size:14px}
.vb-krd .kc-card__text{font-size:12px}
.vb-krd .kc-card__price{font-size:13px}
.vb-krd .kc-card__btn{height:40px;font-size:13px}
.vb-krd .kc-cta{margin-top:48px;padding-bottom:56px}
.vb-krd .kc-cta__box{min-height:0;padding:28px 20px 32px;border-radius:24px;background:linear-gradient(90deg,rgba(36,57,59,.94) 0%,rgba(36,57,59,.75) 65%,rgba(36,57,59,.2) 100%),#24393b url(img/Content2_1-32346136.webp) 78% center/cover no-repeat}
.vb-krd .kc-cta h2{font-size:19px}
.vb-krd .kc-cta p{margin-bottom:20px}
}
@media (max-width:339px){.vb-krd .kc-grid{grid-template-columns:1fr}}
/* планшет 640–959: та же колонка по центру, что у главной (--krd-col задаёт js/main.js) */
@media (min-width:640px) and (max-width:959px){.vb-krd .kc-wrap{max-width:var(--krd-col,none);padding-left:var(--krd-inset,20px);padding-right:var(--krd-inset,20px)}.vb-krd .kc-chips{margin-left:0;margin-right:0;padding-left:0;padding-right:0}.vb-krd .kc-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""

# Скрипт без знака «меньше»: сборщик чистит атрибуты регуляркой по тегам.
JS = r"""
(function () {
  var root = document.getElementById('kd-catalog');
  if (!root) return;
  var groups = [].slice.call(root.querySelectorAll('[data-kc-group]'));
  var cards = [].slice.call(root.querySelectorAll('.kc-card'));
  var search = root.querySelector('[data-kc-search]');
  var sort = root.querySelector('[data-kc-sort]');
  var empty = root.querySelector('.kc-empty');
  var list = root.querySelector('.kc-list');
  var current = 'all';
  var wrap = root.querySelector('.kc-wrap');
  function fit() {
    var w = document.documentElement.clientWidth;
    wrap.style.zoom = w >= 960 && w !== 1200 ? String(w / 1200) : '';
  }
  fit();
  window.addEventListener('resize', fit);

  function apply() {
    var q = (search.value || '').trim().toLowerCase();
    var shown = 0;
    groups.forEach(function (g) {
      var id = g.getAttribute('data-kc-group');
      var inCat = current === 'all' || current === id;
      if (g.hasAttribute('data-kc-off')) { g.hidden = current !== 'all' || !!q; return; }
      var n = 0;
      [].slice.call(g.querySelectorAll('.kc-card')).forEach(function (c) {
        var hit = !q || c.getAttribute('data-kc-name').indexOf(q) !== -1 ||
          c.querySelector('.kc-card__text').textContent.toLowerCase().indexOf(q) !== -1;
        c.hidden = !hit;
        if (hit) n++;
      });
      g.hidden = !inCat || !n;
      if (!g.hidden) shown += n;
    });
    empty.classList.toggle('is-shown', !shown);
    list.classList.toggle('kc-mode-one', current !== 'all');
  }

  function order() {
    var byName = sort.value === 'name';
    groups.forEach(function (g) {
      var grid = g.querySelector('.kc-grid');
      if (!grid) return;
      [].slice.call(grid.children).sort(function (a, b) {
        if (byName) return a.querySelector('.kc-card__title').textContent.localeCompare(b.querySelector('.kc-card__title').textContent, 'ru');
        return a.getAttribute('data-kc-rank') - b.getAttribute('data-kc-rank');
      }).forEach(function (c) { grid.appendChild(c); });
    });
  }

  function show(id, scroll) {
    current = id;
    root.querySelectorAll('[data-kc-show]').forEach(function (b) {
      var on = b.getAttribute('data-kc-show') === id;
      if (b.classList.contains('kc-chip') || b.closest('.kc-side')) {
        b.classList.toggle('is-active', on);
        if (b.classList.contains('kc-chip')) b.setAttribute('aria-pressed', on ? 'true' : 'false');
      }
    });
    var chip = root.querySelector('.kc-chip.is-active');
    if (chip && chip.scrollIntoView && window.matchMedia('(max-width: 959px)').matches) {
      chip.parentNode.scrollTo({ left: chip.offsetLeft - 16, behavior: 'smooth' });
    }
    apply();
    if (scroll) {
      var top = list.getBoundingClientRect().top + window.pageYOffset - 120;
      if (window.pageYOffset > top) window.scrollTo({ top: top, behavior: 'smooth' });
    }
    try { history.replaceState(null, '', id === 'all' ? location.pathname : '#' + id); } catch (e) {}
  }

  root.addEventListener('click', function (e) {
    var b = e.target.closest('[data-kc-show]');
    if (b) { show(b.getAttribute('data-kc-show'), true); return; }
    if (e.target.closest('[data-kc-reset]')) { search.value = ''; show('all', true); return; }
    if (e.target.closest('[data-kc-back]')) {
      if (document.referrer && document.referrer.indexOf(location.host) !== -1) history.back();
      else location.href = window.KRD_SITE_URL ? window.KRD_SITE_URL('/') : '/';
    }
  });
  // «Предзаказ» / «Оставить запрос»: подставляем товар в поп-ап (свой обработчик срабатывает раньше,
  // чем общий на document, который открывает поп-ап)
  cards.forEach(function (c) {
    var btn = c.querySelector('[data-kc-product]');
    btn.addEventListener('click', function () {
      var pop = document.getElementById('krd-pop-' + btn.getAttribute('data-krd-popup'));
      if (!pop) return;
      var v = btn.getAttribute('data-kc-product');
      var field = pop.querySelector('[data-kc-target]');
      var label = pop.querySelector('[data-kc-label]');
      if (field) field.value = v;
      if (label) label.textContent = v;
    });
  });
  search.addEventListener('input', apply);
  sort.addEventListener('change', function () { order(); apply(); });

  var start = (location.hash || '').slice(1);
  show(start && root.querySelector('.kc-chip[data-kc-show="' + start + '"]') ? start : 'all', false);
})();
"""

SEARCH_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="#69979c" stroke-width="2" stroke-linecap="round">'
               '<circle cx="11" cy="11" r="7"></circle><line x1="16.5" y1="16.5" x2="21" y2="21"></line></svg>')

PAGE = (
    '<div id="kd-catalog" class="vb-krd-cat">\n'
    '<main class="kc-wrap">\n'
    '<nav class="kc-crumbs" aria-label="Навигация"><button type="button" data-kc-back>Назад</button><i>|</i>'
    '<a href="/">Главная</a><i>/</i><span>Каталог</span></nav>\n'
    '<div class="kc-top"><div><h1 class="kc-title">Каталог</h1>'
    '<p class="kc-sub">Канаты, стропы, такелаж и комплектующие</p></div>'
    '<div class="kc-help"><button type="button" data-krd-popup="howto">Как выбрать?</button>'
    '<button type="button" data-krd-popup="where">Где применяется?</button></div></div>\n'
    '<div class="kc-layout">\n'
    '<aside class="kc-side"><p class="kc-side__title">Разделы</p><ul>%(side)s</ul></aside>\n'
    '<div class="kc-list">\n'
    '<div class="kc-chips" role="group" aria-label="Разделы">%(chips)s</div>\n'
    '<div class="kc-tools"><label class="kc-search"><input type="search" placeholder="Поиск по каталогу" '
    'aria-label="Поиск по каталогу" data-kc-search>%(icon)s</label>'
    '<label class="kc-sort"><select aria-label="Сортировка" data-kc-sort>'
    '<option value="pop">Сначала популярные</option><option value="name">По названию, А–Я</option>'
    '</select></label></div>\n'
    '%(groups)s\n'
    '<div class="kc-empty"><p>Ничего не нашлось. Попробуйте другой запрос или напишите нам — подберём.</p>'
    '<button type="button" data-kc-reset>Показать весь каталог</button></div>\n'
    '</div>\n</div>\n'
    # баннер как «Остались вопросы?» на главной: та же картинка-фон с крюком, белый текст, кнопка со стрелкой
    '<section class="kc-cta"><div class="kc-cta__box"><h2>Нужна помощь с подбором каната?</h2>'
    '<p>Оставьте заявку, и мы свяжемся с вами в течение 2 часов</p>'
    '<button type="button" data-krd-popup="pick">Получить консультацию'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true"><line x1="7" y1="17" x2="17" y2="7"></line>'
    '<polyline points="8 7 17 7 17 16"></polyline></svg></button></div></section>\n'
    '</main>\n</div>\n'
    '<style>\n%(css)s\n</style>\n'
    '<script>%(js)s</script>\n'
    '<!--krd-pops-->\n%(pops)s\n<!--/krd-pops-->\n'
) % dict(total=total(), ncat=len(CATS), chips=chips(), icon=SEARCH_ICON, side=side(), groups=groups(), css=CSS.strip(), js=JS, pops=POPS)

assert '<' not in JS, 'в скрипте не должно быть «<»'

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, '_doc_catalog.html'), 'w', encoding='utf-8', newline='\n').write(PAGE)
print('== catalog: %d товаров в %d разделах' % (sum(count(c) for c in CATS), len(CATS)))
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'tilda_block.py'), '--doc', 'catalog'], check=True)
