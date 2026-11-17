# Новые иконки из design/icons/new/*.png → img/icon-*.webp в пропорциях иконок с главной:
# предмет ~75% плашки, плашка со скруглёнными углами, прозрачный фон, 144×144 (вдвое больше показа).
# Запуск: python tools/icons_prep.py
import glob, os, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE, FILL, RADIUS = 144, 0.74, 0.24


def prep(src, dst):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    # цвет плашки берём у центра левого края плашки (отступ 22% от края — внутри плашки у всех файлов)
    bg = im.getpixel((int(w * 0.22), h // 2))
    diff = ImageChops.difference(im, Image.new('RGB', im.size, bg)).convert('L')
    # только сам предмет: внутренняя часть картинки, без краёв плашки и рамки
    inner = diff.crop((int(w * .2), int(h * .2), int(w * .8), int(h * .8))).point(lambda v: 255 if v > 18 else 0)
    inner = inner.filter(ImageFilter.MaxFilter(5))
    l, t, r, b = inner.getbbox()
    l += int(w * .2); r += int(w * .2); t += int(h * .2); b += int(h * .2)
    cx, cy = (l + r) / 2, (t + b) / 2
    side = max(r - l, b - t) / FILL
    box = (int(cx - side / 2), int(cy - side / 2), int(cx + side / 2), int(cy + side / 2))
    crop = Image.new('RGB', (box[2] - box[0], box[3] - box[1]), bg)
    crop.paste(im.crop(box), (0, 0))
    crop = crop.resize((SIZE, SIZE), Image.LANCZOS)
    # скруглённая плашка с прозрачными углами (сглаженная маска 4×)
    big = Image.new('L', (SIZE * 4, SIZE * 4), 0)
    ImageDraw.Draw(big).rounded_rectangle((0, 0, SIZE * 4 - 1, SIZE * 4 - 1), radius=int(SIZE * 4 * RADIUS), fill=255)
    out = crop.convert('RGBA')
    out.putalpha(big.resize((SIZE, SIZE), Image.LANCZOS))
    out.save(dst, 'WEBP', quality=90, method=6)
    print('%s → %s (предмет %dx%d px из %dx%d)' % (os.path.relpath(src, ROOT), os.path.relpath(dst, ROOT), r - l, b - t, w, h))


sys.stdout.reconfigure(encoding='utf-8')
for f in sorted(glob.glob(os.path.join(ROOT, 'design', 'icons', 'new', '*.png'))):
    name = os.path.splitext(os.path.basename(f))[0]
    prep(f, os.path.join(ROOT, 'img', 'icon-%s.webp' % name))
