# Страница «Стальные канаты» для Тильды с товарами из каталога Тильды (Магазин → Товары → раздел «Стальные канаты»).
# Вёрстка, стили, фильтры и скрипт — те же, что у статичной страницы (tools/ropes_page.py), но карточки марок
# и списки фильтров строятся в браузере из ответа store.tildaapi.com: заказчик правит товары в Тильде — меняется сайт.
# Клик по карточке ведёт на страницу-шаблон карточки товара /product?p=<uid>&s=<раздел> (tools/product_template.py).
# Запуск: python tools/ropes_page.py (обновит статичную страницу) && python tools/ropes_dynamic.py
#   → tilda/_doc_ropes.html и через tilda_block.py --doc ropes → tilda/ropes.html (код вайб-блока).
import json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ropes_page as rp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tilda', '_doc_steel-ropes.html')
OUT = os.path.join(ROOT, 'tilda', '_doc_ropes.html')
PART = '434043879043'          # раздел «Стальные канаты» в каталоге Тильды
PRODUCT_URL = '/product'       # страница-шаблон карточки товара

ORDERS = {'c': rp.CONSTR_ORDER, 'k': rp.COAT_ORDER, 'l': rp.LAY_ORDER, 'a': rp.APP_ORDER}

# Загрузка товаров и сборка карточек/фильтров. Вставляется перед основным скриптом страницы,
# основной скрипт оборачивается в init() и запускается, когда карточки уже на месте.
# В коде нет символа «<» (так требует сборка): сравнения записаны через «>».
LOADER = r'''
  // номер раздела записан частями: tilda_block.py заменяет длинные числа в коде короткими метками
  var PART = %(part)s, PRODUCT = '%(product)s', ICON = '%(icon)s';
  var ORD = %(orders)s;
  var LAYF = %(layf)s;
  var host = 'store.tildaapi.com';
  function mk(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function arr(v) {
    if (Array.isArray(v)) return v;
    if (typeof v === 'string' && v) { try { var r = JSON.parse(v); return Array.isArray(r) ? r : []; } catch (e) {} }
    return [];
  }
  function num(s) { return parseFloat(String(s).replace(',', '.')) || 0; }
  function lbl(s) { return String(num(s)).replace('.', ','); }
  function present(order, vals) {
    var out = order.filter(function (o) { return vals.indexOf(o) !== -1; });
    vals.slice().sort().forEach(function (v) { if (out.indexOf(v) === -1) out.push(v); });
    return out;
  }
  function baseConstr(s) {
    s = String(s || '').replace(/([0-9A-Za-z])[xх×](?=[0-9A-Za-z])/g, '$1x');
    var m = s.match(/ГОСТ\s*[\d-]+/);
    if (m) return m[0];
    return s.replace(/-(IWRC|PWRC\(K\)|WSC|FC).*$/, '');
  }
  function splitList(s) { return String(s || '').split(',').map(function (x) { return x.trim(); }).filter(function (x) { return x && x !== '—'; }); }
  function nb(v) { return v.replace(/ /g, ' ').replace(/\//g, '/⁠').replace(/–/g, '⁠–⁠'); }

  // товар каталога Тильды → данные марки
  function rope(p, i) {
    var by = {}, apps = {}, common = null;
    arr(p.characteristics).forEach(function (c) {
      by[c.title] = c.value;
      var m = /^Применение, Ø (.+?) мм$/.exec(c.title);
      if (m) m[1].split(';').forEach(function (d) { apps[num(d)] = splitList(c.value); });
      else if (c.title === 'Применение') common = splitList(c.value);
    });
    // ось диаметров: «Диаметр, мм», у ГОСТ-канатов есть ещё «Прочность, Н/мм²» — один диаметр повторяется
    var opts = arr(p.json_options), axis = (opts.filter(function (o) { return o.title === 'Диаметр, мм'; })[0] || opts[0] || {}).title;
    var seen = {};
    var rows = arr(p.editions).map(function (e) {
      var n = num(axis ? e[axis] : '');
      return [lbl(n), apps[n] || common || []];
    }).filter(function (r) { if (!(num(r[0]) > 0) || seen[r[0]]) return false; seen[r[0]] = 1; return true; }).sort(function (a, b) { return num(a[0]) - num(b[0]); });
    var code = by['Марка'] || p.sku || p.title;
    var constr = by['Конструкция'] || '';
    var lay = by['Обозначение свивки'] || '';
    var coat = /^Оцинков/i.test(by['Покрытие проволоки'] || '') ? 'Оцинкованный' : 'Без покрытия';
    var allApps = [];
    rows.forEach(function (r) { r[1].forEach(function (a) { if (allApps.indexOf(a) === -1) allApps.push(a); }); });
    var d0 = rows.length ? rows[0][0] : '', d1 = rows.length ? rows[rows.length - 1][0] : '';
    var rng = d0 === d1 ? d0 : d0 + '–' + d1;
    var strength = by['Временное сопротивление разрыву'] || by['Временное сопротивление разрыву проволоки'] || '';
    return {
      p: p, i: i, code: code, title: p.title || ('Канат ' + constr),
      c: baseConstr(constr), k: by['Тип покрытия'] || '', l: LAYF[lay] || lay, rows: rows, apps: allApps,
      nonrot: by['Некрутящийся канат'] === 'Да',
      text: coat + ', свивка ' + lay + ', ' + nb(strength) + '. Диаметр ' + nb(rng + ' мм') + '.',
      s: [code, code.replace(/x/g, '×'), constr, coat, lay, p.descr || '', allApps.join(' ')].join(' ').toLowerCase()
    };
  }

  function card(r) {
    var url = PRODUCT + '?p=' + r.p.uid + '&s=' + PART;
    var a = mk('article', 'kr-card');
    a.setAttribute('data-kr-i', r.i);
    a.setAttribute('data-kr-c', r.c);
    a.setAttribute('data-kr-k', r.k);
    a.setAttribute('data-kr-l', r.l);
    a.setAttribute('data-kr-rows', JSON.stringify(r.rows));
    a.setAttribute('data-kr-min', r.rows.length ? num(r.rows[0][0]) : 0);
    a.setAttribute('data-kr-s', r.s);
    var ph = mk('a', 'kr-card__ph');
    ph.href = url;
    ph.setAttribute('aria-label', 'Подробнее: ' + r.title + ' ' + r.code);
    if (r.nonrot) ph.appendChild(mk('span', 'kr-card__badge', 'Некрутящийся'));
    var gal = arr(r.p.gallery).map(function (g) { return g.img; }).filter(Boolean);
    var img = mk('img');
    img.src = gal[0] || ICON; img.alt = ''; img.width = 72; img.height = 72; img.loading = 'lazy';
    ph.appendChild(img);
    a.appendChild(ph);
    var h = mk('h3', 'kr-card__title'), ha = mk('a', null, r.title);
    ha.href = url; h.appendChild(ha); a.appendChild(h);
    a.appendChild(mk('p', 'kr-card__code', r.code));
    a.appendChild(mk('p', 'kr-card__text', r.text));
    var prices = arr(r.p.editions).map(function (e) { return num(e.price); }).filter(function (n) { return n > 0; });
    a.appendChild(mk('p', 'kr-card__price', prices.length ? 'от ' + Math.min.apply(null, prices).toLocaleString('ru-RU') + ' ₽' : 'Цена по запросу'));
    var b = mk('button', 'kr-card__btn', 'Предзаказ');
    b.type = 'button';
    b.setAttribute('data-krd-popup', 'order');
    b.setAttribute('data-kr-order', '');
    b.setAttribute('data-kc-product', 'Канат ' + r.code);
    a.appendChild(b);
    var info = mk('div', 'kr-info'); info.hidden = true; a.appendChild(info);
    return a;
  }

  function options(list) {
    var vals = { c: [], k: [], l: [], a: [] };
    list.forEach(function (r) {
      [['c', r.c], ['k', r.k], ['l', r.l]].forEach(function (x) { if (x[1] && vals[x[0]].indexOf(x[1]) === -1) vals[x[0]].push(x[1]); });
      r.apps.forEach(function (ap) { if (vals.a.indexOf(ap) === -1) vals.a.push(ap); });
    });
    Object.keys(vals).forEach(function (g) {
      var ul = root.querySelector('[data-kr-list="' + g + '"]');
      if (!ul) return;
      ul.textContent = '';
      present(ORD[g], vals[g]).forEach(function (v) {
        var li = mk('li'), lab = mk('label', 'kr-f-opt'), inp = mk('input');
        inp.type = 'checkbox'; inp.setAttribute('data-kr-f', g); inp.setAttribute('data-kr-v', v);
        lab.appendChild(inp); lab.appendChild(mk('i')); lab.appendChild(mk('span', null, v));
        var em = mk('em'); em.setAttribute('data-kr-n', ''); lab.appendChild(em);
        li.appendChild(lab); ul.appendChild(li);
      });
    });
  }

  function subline(list) {
    var sub = root.querySelector('[data-kr-sub]');
    if (!sub || !list.length) return;
    var ds = [];
    list.forEach(function (r) { r.rows.forEach(function (x) { var n = num(x[0]); if (ds.indexOf(n) === -1) ds.push(n); }); });
    ds.sort(function (a, b) { return a - b; });
    var n = list.length, a = n %% 10, b = n %% 100;
    var word = (b >= 11 && 14 >= b) ? 'позиций' : a === 1 ? 'позиция' : (a >= 2 && 4 >= a) ? 'позиции' : 'позиций';
    sub.textContent = n + ' ' + word + ', диаметр от ' + lbl(ds[0]) + ' до ' + lbl(ds[ds.length - 1]) + ' мм, другие — по запросу.';
  }

  function recid() { var r = root.closest('.r'); return r ? String(r.id || '').replace('rec', '') : ''; }
  function fail() {
    var g = root.querySelector('.kr-grid');
    g.textContent = '';
    g.appendChild(mk('p', 'kr-load', 'Не удалось загрузить каталог. Обновите страницу или оставьте заявку — подберём канат.'));
    root.querySelectorAll('[data-kr-total]').forEach(function (e) { e.textContent = '—'; });
  }
  function get(slice, acc, tries) {
    var url = 'https://' + host + '/api/getproductslist/?storepartuid=' + PART + '&recid=' + encodeURIComponent(recid()) +
      '&c=' + Date.now() + '&getparts=false&getoptions=false&slice=' + slice + '&size=100';
    fetch(url).then(function (r) { return r.json(); }).then(function (d) {
      if (d && d.redirectto && !tries) { host = host.split('.').slice(0, -1).join('.') + '.' + d.redirectto; get(slice, acc, 1); return; }
      acc = acc.concat((d && d.products) || []);
      if (d && d.nextslice) { get(+d.nextslice, acc, tries); return; }
      if (!acc.length) { fail(); return; }
      var list = acc.map(rope).filter(function (r) { return r.rows.length; });
      var grid = root.querySelector('.kr-grid');
      grid.textContent = '';
      list.forEach(function (r) { grid.appendChild(card(r)); });
      options(list);
      subline(list);
      init();
    }).catch(fail);
  }
'''

INIT_HEAD = "  var grid = root.querySelector('.kr-grid');"
INIT_TAIL = "  paintRange();\n  apply();\n})();"


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    s = open(SRC, encoding='utf-8').read()
    # карточки марок — из каталога: сетка пустая, на время загрузки — подпись
    s, n = re.subn(r'(<div class="kr-grid">).*?(</div>\n<div class="kc-empty">)',
                   r'\1<p class="kr-load">Загружаем каталог…</p>\2', s, count=1, flags=re.S)
    assert n == 1, 'нет сетки карточек'
    # списки фильтров — тоже из каталога
    groups = iter('ckla')
    s, n = re.subn(r'<ul class="kr-f-list">.*?</ul>', lambda m: '<ul class="kr-f-list" data-kr-list="%s"></ul>' % next(groups), s, flags=re.S)
    assert n == 4, 'фильтров не 4: %d' % n
    # подзаголовок: число марок и диаметры считаются из каталога
    s, n = re.subn(r'(<p class="kc-sub">.*?<br>)(.*?)(</p>)', r'\1<span data-kr-sub>\2</span>\3', s, count=1, flags=re.S)
    assert n == 1, 'нет подзаголовка'
    s = s.replace('id="kd-catalog"', 'id="kd-catalog" data-kr-dynamic', 1)
    # скрипт: загрузка + прежний скрипт страницы внутри init()
    a = s.index('<script>') + len('<script>'); b = s.index('</script>', a)
    js = s[a:b]
    assert INIT_HEAD in js and INIT_TAIL in js, 'скрипт страницы изменился — обновите ropes_dynamic.py'
    js = js.replace("a: r[1].map(function (i) { return APPS[i]; })", 'a: r[1]')
    loader = LOADER % dict(part="['%s', '%s'].join('')" % (PART[:6], PART[6:]), product=PRODUCT_URL, icon=rp.ICON,
                           orders=json.dumps(ORDERS, ensure_ascii=False),
                           layf=json.dumps(rp.LAY_FILTER, ensure_ascii=False))
    js = js.replace(INIT_HEAD, loader + '\n  function init() {\n' + INIT_HEAD, 1)
    js = js.replace(INIT_TAIL, "  lo.max = hi.max = String(LAST);\n  hi.value = String(LAST);\n  paintRange();\n  apply();\n  }\n  get(1, [], 0);\n})();", 1)
    assert '<' not in js, 'в скрипте не должно быть «<»'
    s = s[:a] + js + s[b:]
    # подпись загрузки
    i = s.index('</style>')
    s = s[:i] + '.vb-krd .kr-load{grid-column:1/-1;margin:24px 0;color:var(--kc-muted);font-size:14px}\n' + s[i:]
    open(OUT, 'w', encoding='utf-8', newline='\n').write(s)
    print('ok ->', os.path.relpath(OUT, ROOT))
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'tilda_block.py'), '--doc', 'ropes'], check=True)


if __name__ == '__main__':
    main()
