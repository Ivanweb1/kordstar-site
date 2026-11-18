# Новые иконки из design/icons/new/*.png → img/icon-*.webp в стиле иконок с главной:
# ровная плашка того же цвета, что на главной (#f1f7fa), предмет ~68% плашки, чуть больше контраста
# (на главной у предметов тёмные контуры), скруглённые углы, прозрачный фон, 144×144 (вдвое больше показа).
# Запуск: python tools/icons_prep.py
import glob, os, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE, FILL, RADIUS = 144, 0.68, 0.24
TILE = (241, 247, 250)   # цвет плашки иконок на главной
CONTRAST = 1.35          # насколько усилить отличие предмета от плашки


def object_box(im, bg):
    """Рамка предмета: предмет бирюзовый, плашка почти белая — ищем по насыщенности цвета.
    Край картинки (8%) не смотрим: там бывает ободок плашки."""
    w, h = im.size
    m = 0.08
    x0, y0 = int(w * m), int(h * m)
    sat = im.convert('HSV').split()[1].crop((x0, y0, int(w * (1 - m)), int(h * (1 - m))))
    mask = sat.point(lambda v: 255 if v > 45 else 0).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(5))
    l, t, r, b = mask.getbbox()
    return l + x0, t + y0, r + x0, b + y0


def prep(src, dst):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    # фон плашки в исходнике неровный: оцениваем его сильным размытием по кольцу вокруг предмета
    bg = im.getpixel((w // 2, int(h * 0.14)))  # над предметом: сбоку широкий предмет (грузовик) закрывает фон
    l, t, r, b = object_box(im, bg)
    cx, cy = (l + r) / 2, (t + b) / 2
    side = max(r - l, b - t) / FILL
    box = (int(cx - side / 2), int(cy - side / 2), int(cx + side / 2), int(cy + side / 2))
    crop = Image.new('RGB', (box[2] - box[0], box[3] - box[1]), bg)
    # берём только ту часть, что есть в исходнике: за краем картинки Pillow отдаёт чёрное
    inner = (max(box[0], 0), max(box[1], 0), min(box[2], w), min(box[3], h))
    crop.paste(im.crop(inner), (inner[0] - box[0], inner[1] - box[1]))
    crop = crop.resize((SIZE * 2, SIZE * 2), Image.LANCZOS)
    n = SIZE * 2
    # локальный фон: размытая копия, где предмет закрашен цветом плашки исходника
    diff = ImageChops.difference(crop, Image.new('RGB', crop.size, bg)).convert('L')
    obj = diff.point(lambda v: 255 if v > 14 else 0).filter(ImageFilter.MaxFilter(7))
    local_bg = Image.composite(Image.new('RGB', crop.size, bg), crop, obj).filter(ImageFilter.GaussianBlur(n / 10))
    # предмет = отличие от локального фона, перенесённое на плашку главной с усиленным контрастом
    px, lb = crop.load(), local_bg.load()
    out = Image.new('RGB', crop.size, TILE)
    op = out.load()
    for y in range(n):
        for x in range(n):
            p, q = px[x, y], lb[x, y]
            op[x, y] = tuple(max(0, min(255, round(TILE[i] + (p[i] - q[i]) * CONTRAST))) for i in range(3))
    out = out.resize((SIZE, SIZE), Image.LANCZOS)
    big = Image.new('L', (SIZE * 4, SIZE * 4), 0)
    ImageDraw.Draw(big).rounded_rectangle((0, 0, SIZE * 4 - 1, SIZE * 4 - 1), radius=int(SIZE * 4 * RADIUS), fill=255)
    out = out.convert('RGBA')
    out.putalpha(big.resize((SIZE, SIZE), Image.LANCZOS))
    out.save(dst, 'WEBP', quality=90, method=6)
    print('%s → %s' % (os.path.relpath(src, ROOT), os.path.relpath(dst, ROOT)))


sys.stdout.reconfigure(encoding='utf-8')
# только иконки сайта; черновики генераций (*-v2.png и т.п.) в той же папке не трогаем
for name in ('delivery', 'docs', 'warranty'):
    f = os.path.join(ROOT, 'design', 'icons', 'new', name + '.png')
    prep(f, os.path.join(ROOT, 'img', 'icon-%s.webp' % name))
