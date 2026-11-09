# -*- coding: utf-8 -*-
"""Страницы «Политика конфиденциальности» (/policy) и «Согласие на обработку ПДн» (/soglasie).

Запуск:  python tools/docs_pages.py
Пишет код вайб-блоков tilda/policy.html и tilda/soglasie.html (по одному блоку на страницу Тильды)
и превью tilda/policy-preview.html, tilda/soglasie-preview.html.
Реквизиты оператора — только то, что есть в подвале сайта (без ИНН и ОГРН).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tilda')

COMPANY = 'ООО «КОРДСТАР»'
ADDRESS = 'г. Москва, ул. Народная, д. 11, стр. 1, оф. 4И, пом. 86'
EMAIL = 'info@cordstar.ru'
PHONE = '+7 (495) 150-92-22'
PHONE_HREF = '+74951509222'
SITE = 'cordstar.ru'
DATE = '09.11.2026'
LOGO = 'https://optim.tildacdn.com/tild3138-3133-4466-b364-353837636662/-/format/webp/image.png.webp'

CONTACTS = ('{c}, адрес: {a}, e-mail: <a href="mailto:{e}">{e}</a>, телефон: '
            '<a href="tel:{ph}">{p}</a>').format(c=COMPANY, a=ADDRESS, e=EMAIL, ph=PHONE_HREF, p=PHONE)

POLICY = [
    ('1. Общие положения', [
        'Настоящая политика конфиденциальности (далее — Политика) определяет порядок обработки и меры по защите '
        'персональных данных посетителей сайта {s} (далее — Сайт) и составлена в соответствии с Федеральным законом '
        'от 27.07.2006 № 152-ФЗ «О персональных данных».'.format(s=SITE),
        'Оператор персональных данных — ' + CONTACTS + ' (далее — Оператор).',
        'Используя Сайт и отправляя данные через формы на Сайте, посетитель соглашается с условиями Политики. '
        'Если посетитель не согласен с ними, ему следует не отправлять свои данные через Сайт.',
    ]),
    ('2. Какие данные обрабатываются', [
        'Данные, которые посетитель сам указывает в формах Сайта: имя, номер телефона, адрес электронной почты, '
        'а также сведения о заявке — раздел каталога, описание задачи, марка и модель техники, текст вопроса.',
        'Технические данные, которые передаются автоматически: файлы cookie, IP-адрес, сведения о браузере и устройстве, '
        'адреса просмотренных страниц, дата и время посещения.',
    ]),
    ('3. Цели обработки', [
        'Обработка заявок и обращений, обратная связь с посетителем.',
        'Подбор продукции, расчёт стоимости, консультации, предоставление документации.',
        'Заключение и исполнение договоров с посетителем.',
        'Обеспечение работы Сайта и улучшение его работы.',
    ]),
    ('4. Правовые основания', [
        'Согласие посетителя на обработку персональных данных, которое он даёт, отправляя форму на Сайте.',
        'Необходимость заключения и исполнения договора, стороной которого является посетитель.',
    ]),
    ('5. Как обрабатываются данные', [
        'Оператор собирает, записывает, систематизирует, хранит, уточняет, использует, удаляет и уничтожает '
        'персональные данные с использованием средств автоматизации и без них.',
        'Сайт работает на платформе Tilda Publishing: данные из форм передаются Оператору через сервисы этой платформы.',
        'Оператор не передаёт персональные данные третьим лицам, кроме случаев, предусмотренных законодательством '
        'Российской Федерации, и случаев, когда это нужно для исполнения обязательств перед посетителем '
        '(например, для доставки заказа).',
        'Оператор принимает необходимые правовые, организационные и технические меры для защиты персональных данных '
        'от неправомерного доступа, изменения, распространения и уничтожения.',
    ]),
    ('6. Сроки хранения', [
        'Персональные данные хранятся до достижения целей обработки либо до отзыва посетителем согласия на их обработку, '
        'если более длительный срок не требуется по закону.',
    ]),
    ('7. Файлы cookie', [
        'Сайт использует файлы cookie — небольшие файлы, которые сохраняются в браузере и нужны для корректной работы Сайта '
        'и сбора обезличенной статистики посещений.',
        'Посетитель может отключить cookie в настройках браузера; при этом часть функций Сайта может работать некорректно.',
    ]),
    ('8. Права посетителя', [
        'Посетитель вправе получить сведения об обработке своих персональных данных, потребовать их уточнения, '
        'блокирования или уничтожения, если данные неполные, устаревшие, неточные или обрабатываются незаконно.',
        'Посетитель вправе отозвать согласие на обработку персональных данных, направив Оператору письмо на '
        '<a href="mailto:{e}">{e}</a>.'.format(e=EMAIL),
    ]),
    ('9. Заключительные положения', [
        'Оператор вправе изменять Политику. Новая редакция действует с момента её размещения на Сайте.',
        'Вопросы по Политике и обработке персональных данных можно направить на '
        '<a href="mailto:{e}">{e}</a>.'.format(e=EMAIL),
    ]),
]

CONSENT_INTRO = [
    'Отправляя форму на сайте {s}, я свободно, своей волей и в своём интересе даю согласие {c} '
    '(адрес: {a}; далее — Оператор) на обработку моих персональных данных на следующих условиях.'.format(
        s=SITE, c=COMPANY, a=ADDRESS),
]
CONSENT = [
    ('Какие данные', [
        'Имя, номер телефона, адрес электронной почты, а также сведения, которые я указываю в заявке: '
        'раздел каталога, описание задачи, марка и модель техники, текст вопроса.',
    ]),
    ('Для чего', [
        'Для обработки моей заявки, связи со мной, подбора продукции, расчёта стоимости, консультаций, '
        'предоставления документации, а также для заключения и исполнения договора.',
    ]),
    ('Какие действия', [
        'Сбор, запись, систематизация, накопление, хранение, уточнение, извлечение, использование, '
        'блокирование, удаление и уничтожение — с использованием средств автоматизации и без них.',
    ]),
    ('Срок действия', [
        'Согласие действует до достижения целей обработки или до его отзыва.',
        'Я могу отозвать согласие, направив Оператору письмо на <a href="mailto:{e}">{e}</a>.'.format(e=EMAIL),
    ]),
    ('Подтверждение', [
        'Я подтверждаю, что ознакомлен(а) с <a href="/policy">политикой конфиденциальности</a> и что указанные мной '
        'данные принадлежат мне.',
    ]),
]

CSS = """
.vb-krd-doc{display:block;background:#f4f8f9;color:#203133;font-family:"Montserrat",Arial,sans-serif;-webkit-font-smoothing:antialiased}
.vb-krd-doc *,.vb-krd-doc *::before,.vb-krd-doc *::after{box-sizing:border-box}
.vb-krd-doc .kd-top{background:#fff;border-bottom:1px solid #d9e4e6}
.vb-krd-doc .kd-top__in{max-width:1200px;margin:0 auto;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.vb-krd-doc .kd-logo img{display:block;height:56px;width:auto}
.vb-krd-doc .kd-back{display:inline-flex;align-items:center;gap:8px;padding:10px 20px;border:1px solid rgba(101,149,155,.4);border-radius:30px;color:#457c82;font-size:14px;font-weight:500;text-decoration:none;transition:background-color .2s ease}
.vb-krd-doc .kd-back:hover{background:#f4f8f9}
.vb-krd-doc .kd-wrap{max-width:880px;margin:0 auto;padding:56px 24px 88px}
.vb-krd-doc .kd-card{background:#fff;border-radius:24px;padding:48px 56px}
.vb-krd-doc .kd-kicker{margin:0 0 12px;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#69979c}
.vb-krd-doc h1{margin:0 0 12px;font-family:"Montserrat",Arial,sans-serif;font-size:36px;line-height:1.15;font-weight:600;color:#203133}
.vb-krd-doc .kd-date{margin:0 0 32px;font-size:14px;color:#5f7375}
.vb-krd-doc h2{margin:36px 0 14px;font-family:"Montserrat",Arial,sans-serif;font-size:20px;line-height:1.3;font-weight:600;color:#203133}
.vb-krd-doc p{margin:0 0 12px;font-size:16px;line-height:1.65;color:#203133}
.vb-krd-doc ul{margin:0 0 12px;padding:0 0 0 22px}
.vb-krd-doc li{margin:0 0 8px;font-size:16px;line-height:1.65;color:#203133}
.vb-krd-doc li::marker{color:#457c82}
.vb-krd-doc a{color:#457c82;text-decoration:underline;text-underline-offset:2px}
.vb-krd-doc a[href^="tel:"]{white-space:nowrap}
.vb-krd-doc .kd-foot{margin-top:40px;padding-top:24px;border-top:1px solid #d9e4e6;font-size:14px;line-height:1.6;color:#5f7375}
@media (max-width:640px){
.vb-krd-doc .kd-top__in{padding:12px 16px}
.vb-krd-doc .kd-logo img{height:44px}
.vb-krd-doc .kd-back{padding:8px 14px;font-size:13px}
.vb-krd-doc .kd-wrap{padding:24px 12px 56px}
.vb-krd-doc .kd-card{padding:28px 20px;border-radius:20px}
.vb-krd-doc h1{font-size:26px}
.vb-krd-doc h2{font-size:18px;margin-top:28px}
.vb-krd-doc p,.vb-krd-doc li{font-size:15px}
}
"""

FONTS = ("@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap');")


def sections(items, as_list):
    out = []
    for title, paras in items:
        out.append('<h2>%s</h2>' % title)
        if as_list and len(paras) > 1:
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % p for p in paras))
        else:
            out.extend('<p>%s</p>' % p for p in paras)
    return '\n'.join(out)


def page(sid, kicker, title, body):
    return (
        '<section id="%s" class="vb-krd-doc" data-vibeblock-unique-section="yes" aria-label="%s">\n'
        '<header class="kd-top"><div class="kd-top__in">'
        '<a class="kd-logo" href="/" aria-label="Кордстар — на главную"><img src="%s" alt="Кордстар"></a>'
        '<a class="kd-back" href="/">← На главную</a></div></header>\n'
        '<main class="kd-wrap"><article class="kd-card">\n'
        '<p class="kd-kicker">%s</p><h1>%s</h1><p class="kd-date">Редакция от %s</p>\n%s\n'
        '<div class="kd-foot">%s</div>\n'
        '</article></main>\n</section>\n<style>\n%s%s\n</style>\n'
    ) % (sid, title, LOGO, kicker, title, DATE, body, 'Оператор: ' + CONTACTS, FONTS, CSS.strip())


def preview(code, title):
    return ('<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            '<meta name="robots" content="noindex, nofollow"><title>%s</title>'
            '<style>body{margin:0}</style></head><body>\n%s</body></html>') % (title, code)


docs = {
    'policy': page('vb-krd-policy', 'Документы', 'Политика конфиденциальности', sections(POLICY, True)),
    'soglasie': page('vb-krd-consent', 'Документы', 'Согласие на обработку персональных данных',
                     '\n'.join('<p>%s</p>' % p for p in CONSENT_INTRO) + '\n' + sections(CONSENT, False)),
}
titles = {'policy': 'Политика конфиденциальности', 'soglasie': 'Согласие на обработку персональных данных'}

os.makedirs(OUT, exist_ok=True)
for name, code in docs.items():
    open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8', newline='\n').write(code)
    open(os.path.join(OUT, name + '-preview.html'), 'w', encoding='utf-8', newline='\n').write(preview(code, titles[name]))
    print('%s: %d КБ -> tilda/%s.html' % (titles[name], len(code.encode()) // 1024, name))
