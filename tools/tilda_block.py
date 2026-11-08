# -*- coding: utf-8 -*-
"""Собирает главную в ОДИН код для вайб-блока Тильды (tpl 1370).

Запуск:  python tools/tilda_block.py

Что делает:
  * берёт разметку страницы (всё внутри #allrecords) и оборачивает её в
    <section class="vb-krd"> — чтобы не конфликтовать с #allrecords самой Тильды;
  * из 1,2 МБ CSS оставляет только правила, которые реально срабатывают на этой
    разметке (или на классах, которые добавляет скрипт), и все селекторы
    ограничивает контейнером .vb-krd — остальные блоки страницы не задеваются;
  * выкидывает служебные data-атрибуты Zero-блоков, которые нужны только
    редактору Тильды (их ~340 КБ), и data-original, чтобы ленивая загрузка
    Тильды не трогала картинки;
  * картинки берёт с CDN Тильды (исходные адреса — из reference/index.html);
  * скрипт js/main.js кладёт внутрь одной обёртки (function(){ ... })();
  * пишет tilda/kordstar-main.html — это и есть код блока,
    и tilda/preview.html — проверка блока на «пустой странице Тильды».
"""
import os, re, sys
import tinycss2
from lxml import html as LH
from cssselect import GenericTranslator, SelectorError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tilda')
SCOPE = '.vb-krd'
SECTION_ID = 'vb-krd-page'
LIMIT = 1024 * 1024  # Тильда не сохраняет код вайб-блока больше 1 МБ

FONTS = ("@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@100..900"
         "&family=Inter:wght@300;400;500;600;700&display=swap');")


def read(p):
    return open(os.path.join(ROOT, p), encoding='utf-8').read()


# ---------- картинки: локальный файл -> CDN Тильды ----------
def cdn_map():
    ref = read('reference/index.html')
    m = {}
    for tid, rest in re.findall(r'tildacdn\.com/(til[da][0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f-]+)/([^"\'\s)&]+)', ref):
        fname = rest.split('/')[-1]
        fname = re.sub(r'\.(png|jpe?g)\.webp$', r'.\1', fname)
        key = tid[4:8] + tid[9:13]
        if fname.endswith('.svg'):
            m[key] = 'https://static.tildacdn.com/%s/%s' % (tid, fname)
        else:
            m[key] = 'https://optim.tildacdn.com/%s/-/format/webp/%s.webp' % (tid, fname)
    return m


CDN = cdn_map()
MISSING = set()


def img_url(local):
    """img/Name-XXXXXXXX.ext -> адрес на CDN Тильды"""
    name = local.split('/')[-1]
    mm = re.search(r'-([0-9a-f]{8})\.\w+$', name)
    if mm and mm.group(1) in CDN:
        return CDN[mm.group(1)]
    MISSING.add(local)
    return 'https://ivanweb1.github.io/kordstar-site/img/' + name  # запасной вариант


def fix_urls(text):
    return re.sub(r'(?:\.\./)?img/[\w.-]+\.(?:webp|png|jpe?g|svg|gif)', lambda m: img_url(m.group(0)), text)


# ---------- разметка ----------
src = read('index.html')
doc = LH.fromstring(src)
body = re.search(r'<!--allrecords-->\s*(<div id="allrecords".*?)<script src="js/main.js">', src, re.S).group(1)
inner = re.sub(r'^<div id="allrecords"[^>]*>', '', body.strip())
inner = re.sub(r'</div>\s*(?:<!--/allrecords-->)?\s*$', '', inner.strip())

# ---------- скрипт ----------
js = read('js/main.js')
# слова из строк скрипта: классы, которые он навешивает (is-open, t-animate_started …)
js_words = set()
for s in re.findall(r"'([^'\n]*)'|\"([^\"\n]*)\"|`([^`]*)`", js):
    for part in s:
        js_words.update(re.findall(r'[\w-]+', part))

# ---------- CSS: чистка неиспользуемого ----------
css_src = '\n'.join(read(p) for p in ('css/page.css', 'css/fixes.css', 'css/type-scale.css'))
TR = GenericTranslator()
cache = {}
doc_root = doc.getroottree()


def strip_pseudo(sel):
    # :hover, ::before, :not(...), :nth-child(...) — убираем; это только расширяет выборку
    s = sel
    for _ in range(3):
        s = re.sub(r'::?[\w-]+\((?:[^()]|\([^()]*\))*\)', '', s)
    s = re.sub(r'::?[\w-]+', '', s)
    # классы, которые добавляет скрипт, в исходной разметке ещё нет — не требуем их
    s = re.sub(r'\.([\w-]+)', lambda m: '' if m.group(1) in js_words else m.group(0), s)
    s = re.sub(r'\s*([>+~])\s*(?=[>+~,]|$)', ' ', s)          # висящие комбинаторы
    s = re.sub(r'(^|[\s>+~])(?=[\s>+~]|$)', r'\1*', s)          # пустые составные -> *
    s = re.sub(r'\s+', ' ', s).strip()
    return s or '*'


def used(sel):
    s = strip_pseudo(sel)
    if s in cache:
        return cache[s]
    try:
        xp = TR.css_to_xpath(s)
        r = bool(doc.xpath(xp))
    except (SelectorError, Exception):
        r = True  # не смогли разобрать — оставляем
    cache[s] = r
    return r


ROOT_SEL = re.compile(r'^(?:html|:root|body|\.t-body|body\.t-body|#allrecords|\.t-records)(?=$|[\s>+~.:#\[])')


def scope(sel):
    sel = sel.strip()
    if re.match(r'#rec\d+(?=$|[\s>+~.:#\[])', sel):
        return sel
    m = ROOT_SEL.match(sel)
    if m:
        rest = sel[m.end():]
        # «body .x» -> «.vb-krd .x», «.t-records.t-records_animated» -> «.vb-krd»
        rest = re.sub(r'^(?:\.t-records_[\w-]+|\.t-records|\.t-body)+', '', rest)
        r2 = ROOT_SEL.match(rest.lstrip())
        if r2 and rest[:1].isspace():  # «html body …»
            rest = rest.lstrip()[r2.end():]
        return SCOPE + rest
    return SCOPE + ' ' + sel


def split_selectors(prelude):
    out, depth, cur = [], 0, ''
    for ch in prelude:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return [s.strip() for s in out if s.strip()]


def minify_decls(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s*([;:{},])\s*', r'\1', text)
    return text.rstrip(';')


stats = {'kept': 0, 'dropped': 0}
keyframes, fontfaces = {}, []
entries = []  # (условие @media/@supports, селекторы, свойства) в исходном порядке


def walk(rules, ctx=()):
    for r in rules:
        if r.type == 'qualified-rule':
            prelude = tinycss2.serialize(r.prelude).strip()
            sels = split_selectors(prelude)
            keep = [s for s in sels if used(s)]
            if not keep:
                stats['dropped'] += 1
                continue
            stats['kept'] += 1
            decl = minify_decls(tinycss2.serialize(r.content))
            if decl:
                entries.append((ctx, ','.join(scope(s) for s in keep), decl))
        elif r.type == 'at-rule':
            kw = r.lower_at_keyword
            prelude = re.sub(r'/\*.*?\*/', '', tinycss2.serialize(r.prelude), flags=re.S)
            prelude = re.sub(r'\s+', ' ', prelude).strip()
            if kw in ('media', 'supports', 'container', 'layer') and r.content is not None:
                walk(tinycss2.parse_rule_list(r.content, skip_comments=True, skip_whitespace=True),
                     ctx + ('@%s %s' % (kw, prelude),))
            elif kw in ('keyframes', '-webkit-keyframes'):
                keyframes[(kw, prelude)] = '@%s %s{%s}' % (kw, prelude, minify_decls(tinycss2.serialize(r.content)))
            elif kw == 'font-face':
                fontfaces.append('@font-face{%s}' % minify_decls(tinycss2.serialize(r.content)))
            # @import, @charset, @page — не нужны


walk(tinycss2.parse_stylesheet(css_src, skip_comments=True, skip_whitespace=True))

# одинаковое правило при одинаковом условии: побеждает последнее, ранние копии лишние
last = {}
for i, e in enumerate(entries):
    last[e] = i
entries = [e for i, e in enumerate(entries) if last[e] == i]


def emit(items):
    """идущие подряд правила с одним условием кладём в один @media"""
    out, i = [], 0
    while i < len(items):
        ctx = items[i][0]
        if not ctx:
            out.append('%s{%s}' % items[i][1:]); i += 1; continue
        head = ctx[0]; j = i
        while j < len(items) and items[j][0][:1] == (head,):
            j += 1
        inner_ = [(e[0][1:],) + e[1:] for e in items[i:j]]
        out.append('%s{%s}' % (head, emit(inner_)))
        i = j
    return ''.join(out)


# соседние правила с тем же селектором и условием склеиваем в одно
merged = []
for e in entries:
    if merged and merged[-1][0] == e[0] and merged[-1][1] == e[1]:
        merged[-1] = (e[0], e[1], merged[-1][2] + ';' + e[2])
    else:
        merged.append(e)
entries = merged

css = emit(entries)

# анимации: только те, что упоминаются в оставшемся CSS или в скрипте
anim = ''
for (kw, name), text in keyframes.items():
    if re.search(r'(?<![\w-])%s(?![\w-])' % re.escape(name), css + js):
        anim += text
# свои шрифты: только семейства, которые где-то используются
ff = ''
for f in fontfaces:
    fam = re.search(r"font-family:\s*['\"]?([^;'\"]+)", f)
    if fam and fam.group(1).strip() in css:
        ff += f
css = fix_urls(FONTS + ff + css + anim)

# корень блока: то, что раньше стояло на body/#allrecords, плюс изоляция box-sizing
css = (SCOPE + '{display:block;position:relative;font-family:var(--t-text-font,"Montserrat",Arial,sans-serif)}'
       ) + css
css = css.replace(FONTS, '')
css = FONTS + css

# ---------- атрибуты: оставляем только нужные стилям и скрипту ----------
need_attrs = set(re.findall(r'\[([\w-]+)', css)) | set(a for a in js_words if a.startswith('data-'))
need_attrs |= {'data-elem-id', 'data-group-id', 'data-elem-type'}


def keep_attr(name):
    if not name.startswith('data-'):
        return True
    if name.startswith('data-artboard-'):  # скрипт читает настройки артборда по имени
        return re.match(r'data-artboard-(upscale|heightmode)', name) is not None
    if name.startswith('data-animate-'):
        return True
    return name in need_attrs


def clean_tag(m):
    tag = m.group(0)
    def attr(a):
        return a.group(0) if keep_attr(a.group(1)) else ''
    return re.sub(r'\s([\w:-]+)(?:="[^"]*")?(?=[\s/>])', attr, tag)


markup = re.sub(r'<!--.*?-->', '', inner, flags=re.S)
markup = re.sub(r'<[a-zA-Z][^<>]*>', clean_tag, markup)
markup = re.sub(r'\sdata-original="[^"]*"', '', markup)
markup = re.sub(r'\sdata-tilda-edit="[^"]*"', '', markup)
markup = fix_urls(markup)
markup = re.sub(r'>\s+<', '> <', markup)
markup = re.sub(r'[ \t]{2,}', ' ', markup)

# ---------- скрипт в одной обёртке ----------
js_out = fix_urls(js)
js_out = re.sub(r'^\s*/\*.*?\*/\s*$', '', js_out, flags=re.S | re.M)
js_out = re.sub(r'\n\s*\n+', '\n', js_out)

# ---------- короткие метки вместо длинных номеров Тильды ----------
# rec3443015601, data-elem-id="1788087136109", molecule-1787765170325000005 … — эти номера
# повторяются в селекторах тысячи раз. Меняем их одинаково в разметке, стилях и скрипте.
URL_RE = re.compile(r'https?://[^\s"\'()<>]+')
ids = []
for n in re.findall(r'\d{10,}', URL_RE.sub(' ', markup)):
    if n not in ids:
        ids.append(n)


def b36(i):
    a = '0123456789abcdefghijklmnopqrstuvwxyz'
    t = ''
    while True:
        t = a[i % 36] + t
        i //= 36
        if not i:
            return 'k' + t


short = {n: b36(i) for i, n in enumerate(ids)}


def shorten(text):
    # адреса картинок не трогаем: в них тоже бывают длинные цифры
    urls = URL_RE.findall(text)
    parts = [re.sub(r'\d{10,}', lambda m: short.get(m.group(0), m.group(0)), p) for p in URL_RE.split(text)]
    out = parts[0]
    for u, p in zip(urls, parts[1:]):
        out += u + p
    return out


markup, css, js_out = shorten(markup), shorten(css), shorten(js_out)
# длинные имена атрибутов тоже
for a, b in (('data-elem-id', 'data-ei'), ('data-group-id', 'data-gi'), ('data-elem-type', 'data-et')):
    markup, css, js_out = markup.replace(a, b), css.replace(a, b), js_out.replace(a, b)

code = (
    '<section id="%s" class="vb-krd" data-section-name="Главная Кордстар" '
    'data-vibeblock-unique-section="yes" aria-label="Кордстар — главная">\n%s\n</section>\n'
    '<style>\n%s\n</style>\n'
    '<script>\n(function () {\n%s\n})();\n</script>\n'
) % (SECTION_ID, markup.strip(), css, js_out.strip())

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, 'kordstar-main.html'), 'w', encoding='utf-8', newline='\n').write(code)

# превью: «страница Тильды» с одним вайб-блоком
preview = ('<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">'
           '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
           '<meta name="robots" content="noindex, nofollow"><title>Превью вайб-блока</title>'
           '<style>body{margin:0;--t-headline-font:"Montserrat",Arial,sans-serif;'
           '--t-text-font:"Montserrat",Arial,sans-serif}*{box-sizing:content-box}</style></head>'
           '<body class="t-body"><div id="allrecords" class="t-records">'
           '<div id="rec999" class="r t-rec" data-record-type="1370">\n%s</div></div></body></html>') % code
open(os.path.join(OUT, 'preview.html'), 'w', encoding='utf-8', newline='\n').write(preview)

size = len(code.encode('utf-8'))
print('CSS правил оставлено: %d, выброшено: %d' % (stats['kept'], stats['dropped']))
print('Разметка: %d КБ, CSS: %d КБ, JS: %d КБ' % (len(markup.encode()) // 1024, len(css.encode()) // 1024, len(js_out.encode()) // 1024))
print('Код блока: %d КБ (лимит Тильды %d КБ) -> tilda/kordstar-main.html' % (size // 1024, LIMIT // 1024))
if MISSING:
    print('Нет на CDN Тильды, взяты с GitHub Pages:', ', '.join(sorted(MISSING)))
if size > LIMIT:
    sys.exit('ВНИМАНИЕ: код больше лимита Тильды')
