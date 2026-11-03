"""Одноразовая конвертация сохранённой Tilda-страницы (MHTML) в статический проект.
Запуск: python tools/convert.py "путь/к/странице.mhtml"
"""
import email, os, re, sys, hashlib
from email import policy

SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG, CSS = os.path.join(ROOT, 'img'), os.path.join(ROOT, 'css')
os.makedirs(IMG, exist_ok=True); os.makedirs(CSS, exist_ok=True)

msg = email.message_from_binary_file(open(SRC, 'rb'), policy=policy.default)
parts, html = {}, None
for p in msg.walk():
    if p.is_multipart(): continue
    loc = p['Content-Location'] or ''
    data = p.get_payload(decode=True) or b''
    if p.get_content_type() == 'text/html' and html is None:
        html = data.decode('utf-8'); continue
    parts[loc] = (p.get_content_type(), data)

EXT = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/svg+xml': 'svg', 'image/webp': 'webp', 'image/gif': 'gif'}
def tild_id(url):
    m = re.search(r'/(til[da][0-9a-f-]+)/', url)
    return m.group(1) if m else None

# картинки: по tild-id, предпочитая самый крупный вариант
images = {}
for loc, (ct, data) in parts.items():
    if ct in EXT:
        tid = tild_id(loc) or hashlib.md5(loc.encode()).hexdigest()[:10]
        if tid not in images or len(data) > len(images[tid][1]):
            fname = loc.rstrip('/').split('/')[-1].replace('.webp', '') if '/-/' in loc else loc.split('/')[-1]
            base = re.sub(r'[^a-zA-Z0-9_-]', '', fname.rsplit('.', 1)[0]).strip('-_')[:28] or 'img'
            images[tid] = (f'{base}-{tid[4:8]}{tid[9:13]}.{EXT[ct]}', data, '/resize/20x/' in loc)
for tid, (name, data, thumb) in images.items():
    if thumb: continue
    open(os.path.join(IMG, name), 'wb').write(data)

def local(url):
    if url.startswith('img/'): return url
    tid = tild_id(url)
    if tid and tid in images and not images[tid][2]: return 'img/' + images[tid][0]
    if tid and '/resize/20x/' in url:  # в файле только размытая превьюшка — берём оригинал с CDN
        return 'https://static.tildacdn.com/' + tid + '/' + url.split('/')[-1]
    return url  # нет в файле — оставляем ссылку на CDN

# CSS в порядке подключения
order = re.findall(r'<link[^>]+href="([^"]+)"[^>]*>', html)
css_out, seen = [], set()
for href in order:
    if href in seen or href not in parts or parts[href][0] != 'text/css': continue
    seen.add(href)
    if 'fonts.googleapis.com' in href: continue
    css = parts[href][1].decode('utf-8', 'replace').replace('@charset "utf-8";', '')
    css = re.sub(r'url\("?([^")]+)"?\)', lambda m: 'url("../' + local(m.group(1)) + '")' if local(m.group(1)).startswith('img/') else m.group(0), css)
    css_out.append(f'/* ---- {href[:90]} ---- */\n{css.strip()}\n')
open(os.path.join(CSS, 'page.css'), 'w', encoding='utf-8').write('\n'.join(css_out))

body = re.search(r'<body[^>]*>(.*)</body>', html, re.S).group(1)
body = re.sub(r'<script\b.*?</script>|<noscript\b.*?</noscript>|<link[^>]*>|<style\b.*?</style>', '', body, flags=re.S)
# убираем инлайн-стили, которые выставлял JS Тильды (позиции/зум под экран сохранения)
STRIP = ('t396__elem', 't396__group', 't396__artboard', 't396__carrier', 't396__filter',
         'tn-molecule__prx-wrapper', 'tn-molecule__sticky-wrapper', 'tn-atom__sbs-anim-wrapper', 't-body')
def clean_tag(m):
    tag = m.group(0)
    cls = re.search(r'class="([^"]*)"', tag)
    if cls and cls.group(1).split()[0] in STRIP:
        tag = re.sub(r'\sstyle="[^"]*"', '', tag)
    else:
        tag = re.sub(r'transform-origin:\s*center center;?\s*', '', tag)
    return tag
body = re.sub(r'<[a-zA-Z][^>]*>', clean_tag, body)
body = re.sub(r'\sstyle="\s*"', '', body)
# ссылки на картинки: data-original — полноразмерный оригинал
body = re.sub(r'(https://(?:static|optim|thb)\.tildacdn\.com/[^"\')\s&]+)', lambda m: local(m.group(1)), body)
open(os.path.join(ROOT, 'src-body.html'), 'w', encoding='utf-8').write(body)
missing = sorted(set(u for u in re.findall(r'https://[a-z]+\.tildacdn\.com/[^"\')\s&]+', body)))
print('images:', len(images), '| css blocks:', len(css_out), '| body:', len(body))
print('not in mhtml:'); print('\n'.join(missing))
