# Шаблон карточки товара из каталога Тильды: tilda/_doc_strop-1sk.html -> tilda/_doc_product.html
# Вёрстка и стили — как у карточки /strop-1sk; название, марка, описание, диаметры, характеристики,
# фото и цена подставляются скриптом из магазина Тильды (Магазин → Товары) по адресу страницы:
#   /product?p=<uid товара>&s=<uid раздела>
# Запуск: python tools/product_template.py && python tools/tilda_block.py --doc product
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tilda', '_doc_strop-1sk.html')
OUT = os.path.join(ROOT, 'tilda', '_doc_product.html')

html = open(SRC, encoding='utf-8').read()


def sub(pattern, repl, count=1):
    global html
    new, n = re.subn(pattern, repl, html, count=count, flags=re.S)
    if n != count:
        raise SystemExit('не найдено: ' + pattern[:80])
    html = new


# корень: id другой, пока товар грузится — класс is-loading
sub(r'<div id="kd-product" class="krd-product">', '<div id="kd-product" class="krd-product is-loading" data-kp-dynamic>')
# хлебные крошки: название товара
sub(r'<span aria-current="page">[^<]*</span>', '<span aria-current="page" data-kp-f="crumb"></span>')
# заголовок, марка, лид
sub(r'<h1 id="kp-title">[^<]*</h1>', '<h1 id="kp-title" data-kp-f="title"></h1>')
sub(r'<p class="kp-code">[^<]*</p>', '<p class="kp-code" data-kp-f="code"></p>')
sub(r'<p class="kp-lead">[^<]*</p>', '<p class="kp-lead" data-kp-f="descr"></p>')
# диаметры: подпись и кнопки — из вариантов товара
sub(r'<div class="kp-diams" role="group" aria-label="Диаметр, мм"><p>Диаметр, мм <span>выберите нужный</span></p><div>.*?</div></div>',
    '<div class="kp-diams" role="group" aria-label="Диаметр, мм" data-kp-f="diams"><p><b data-kp-f="axis">Диаметр, мм</b> <span>выберите нужный</span></p><div data-kp-f="diam-list"></div></div>')
# короткий список параметров
sub(r'(<div class="kp-specs" aria-label="Основные параметры">).*?(\n        </div>)', r'\1\2')
html = html.replace('<div class="kp-specs" aria-label="Основные параметры">', '<div class="kp-specs" aria-label="Основные параметры" data-kp-f="specs">', 1)
# цена
sub(r'<p><span>Стоимость</span><strong>По запросу</strong></p>', '<p><span>Стоимость</span><strong data-kp-f="price">По запросу</strong></p>')
# вкладка «Описание»
sub(r'<h2>Канат 6x19W-IWRC-sZ-Ung-1960</h2><div class="kp-copy"><p>[^<]*</p></div>',
    '<h2 data-kp-f="code-title"></h2><div class="kp-copy"><p data-kp-f="descr2"></p></div>')
sub(r'<ul class="kp-adv">.*?</ul>', '<ul class="kp-adv" data-kp-f="adv"></ul>')
sub(r'<h3 class="kp-sub">Применение</h3>\s*<dl class="kp-table">.*?</dl>',
    '<h3 class="kp-sub" data-kp-f="apps-title">Применение</h3>\n          <dl class="kp-table" data-kp-f="apps"></dl>')
# вкладка «Характеристики»
sub(r'(<h2>Характеристики</h2>)<dl class="kp-table">.*?</dl>', r'\1<dl class="kp-table" data-kp-f="chars"></dl>')
# вкладка «Качество»: сертификаты
sub(r'<dl class="kp-table"><div><dt>Сертификаты</dt><dd>По запросу</dd></div></dl>',
    '<dl class="kp-table"><div><dt>Сертификаты</dt><dd data-kp-f="cert">По запросу</dd></div></dl>')
sub(r'Запросите сертификаты на канат 6x19W-IWRC-sZ-Ung-1960 нужного диаметра\.',
    'Запросите сертификаты на <span data-kp-f="cert-name">товар</span> нужного диаметра.')
# поп-ап предзаказа: товар
sub(r'<b>Канат 6x19W-IWRC-sZ-Ung-1960</b>', '<b data-kp-f="pop-name"></b>')
sub(r'value="Канат 6x19W-IWRC-sZ-Ung-1960"', 'value="" data-kp-f="pop-input"')

# стили: загрузка и ошибка
sub(r'</style>\n<script>', '''.vb-krd .krd-product.is-loading .kp-hero,.vb-krd .krd-product.is-loading .kp-content{opacity:0}
.vb-krd .kp-hero,.vb-krd .kp-content{transition:opacity .3s}
.vb-krd .kp-error{margin:0 0 24px;padding:18px 22px;border-radius:16px;background:#fff;color:var(--kp-deep);font-size:14px;line-height:1.5}
</style>
<script>''')

LOADER = r'''
(function(){
  // Данные карточки — из магазина Тильды: /product?p=<uid товара>&s=<uid раздела>
  var root=document.getElementById('kd-product'); if(!root||!root.hasAttribute('data-kp-dynamic'))return;
  var q=new URLSearchParams(location.search), PID=q.get('p')||'', PART=q.get('s')||'';
  // короткий список параметров — как на карточке /strop-1sk; свивка показывается обозначением (sZ (RHRL))
  var TOP=['Конструкция','Тип покрытия','Направление свивки','Временное сопротивление','Некрутящийся канат'];
  var LAYF={sZ:'sZ (RHRL)',zZ:'zZ (RHLL)',sS:'sS (LHLL)',zS:'zS (LHRL)'};
  function hidden(t){return t==='Марка'||t==='Сертификаты'||t.indexOf('Применение')===0}
  var host='store.tildaapi.com';
  function f(n){return root.querySelector('[data-kp-f="'+n+'"]')}
  function fa(n){return document.querySelectorAll('[data-kp-f="'+n+'"]')}
  function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
  function arr(v){if(Array.isArray(v))return v;if(typeof v==='string'&&v){try{var r=JSON.parse(v);return Array.isArray(r)?r:[]}catch(e){}}return []}
  function num(s){return parseFloat(String(s).replace(',','.'))||0}
  function money(v){var n=num(v);return n>0?n.toLocaleString('ru-RU')+' ₽':''}
  function setText(n,v){[].forEach.call(fa(n),function(e){e.textContent=v})}
  function recid(){var r=root.closest('.r');return r?String(r.id||'').replace('rec',''):''}
  function fail(msg){root.classList.remove('is-loading');var hero=root.querySelector('.kp-hero');var p=el('p','kp-error',msg);hero.parentNode.insertBefore(p,hero);hero.style.display='none';root.querySelector('.kp-content').style.display='none'}
  function richList(html){
    // описание товара из каталога: абзацы -> пункты списка, из разметки сохраняем только жирный
    var doc=new DOMParser().parseFromString('<div>'+(html||'')+'</div>','text/html');
    var blocks=doc.body.querySelectorAll('p,li');var out=[];
    (blocks.length?[].slice.call(blocks):[doc.body]).forEach(function(b){
      var li=el('li');[].forEach.call(b.childNodes,function(n){
        if(n.nodeType===3)li.appendChild(document.createTextNode(n.textContent));
        else if(n.nodeType===1){var t=/^(B|STRONG)$/.test(n.tagName)?el('b',null,n.textContent):document.createTextNode(n.textContent);li.appendChild(t)}
      });if(li.textContent.trim())out.push(li)});
    return out}
  function row(dt,dd,wrap){var d=el('div');d.appendChild(el('dt',null,dt));d.appendChild(el('dd',null,dd));wrap.appendChild(d)}
  function render(p){
    var chars=arr(p.characteristics), by={};
    chars.forEach(function(c){by[c.title]=c.value});
    var code=by['Марка']||p.sku||'';
    document.title=p.title+' — Кордстар';
    setText('title',p.title);setText('crumb',p.title);setText('code',code);f('code').hidden=!code;
    setText('descr',p.descr||'');setText('descr2',p.descr||'');setText('code-title',code?String(p.title).split(' ')[0]+' '+code:p.title);
    var name=code?String(p.title).split(' ')[0]+' '+code:p.title;setText('pop-name',name);setText('cert-name',name);
    [].forEach.call(fa('pop-input'),function(i){i.value=name});
    // варианты (диаметры)
    var opts=arr(p.json_options), axis=opts[0]&&opts[0].title, eds=arr(p.editions);
    var list=f('diam-list');
    if(axis&&eds.length){
      setText('axis',axis);f('diams').setAttribute('aria-label',axis);
      eds.slice().sort(function(a,b){return num(a[axis])-num(b[axis])}).forEach(function(e){
        var b=el('button','kp-d',e[axis]);b.type='button';b.setAttribute('data-kp-d',e[axis]);b.setAttribute('aria-pressed','false');
        b.setAttribute('data-kp-price',e.price||'');list.appendChild(b)});
    } else f('diams').hidden=true;
    // цена: у вариантов или у товара; 0 — «По запросу»
    var prices=eds.map(function(e){return num(e.price)}).filter(function(n){return n>0});
    if(num(p.price)>0)prices.push(num(p.price));
    var base=prices.length?(prices.length>1&&Math.min.apply(null,prices)!==Math.max.apply(null,prices)?'от ':'')+money(Math.min.apply(null,prices)):'По запросу';
    setText('price',base);f('price').setAttribute('data-kp-base',base);
    // короткие параметры
    var specs=f('specs'), shown=0;
    TOP.forEach(function(t){chars.forEach(function(c){if(shown<5&&c.title.indexOf(t)===0){var v=t==='Направление свивки'&&LAYF[by['Обозначение свивки']]||c.value;var d=el('div');d.appendChild(el('span',null,c.title));var i=el('i');i.setAttribute('aria-hidden','true');d.appendChild(i);d.appendChild(el('strong',null,v));specs.appendChild(d);shown++}})});
    if(!shown)chars.filter(function(c){return !hidden(c.title)}).slice(0,5).forEach(function(c){var d=el('div');d.appendChild(el('span',null,c.title));var i=el('i');i.setAttribute('aria-hidden','true');d.appendChild(i);d.appendChild(el('strong',null,c.value));specs.appendChild(d)});
    // описание: преимущества и применение
    var adv=f('adv');richList(p.text).forEach(function(li){adv.appendChild(li)});adv.hidden=!adv.children.length;
    // применение: общее или по группам диаметров («Применение, Ø 8; 9; 10 мм» → «8, 9 и 10 мм»)
    var groups=chars.filter(function(c){return /^Применение, Ø /.test(c.title)});
    groups.forEach(function(c){var ds=c.title.replace(/^Применение, Ø /,'').replace(/ мм$/,'').split(';').map(function(x){return x.trim()});
      row((ds.length>1?ds.slice(0,-1).join(', ')+' и '+ds[ds.length-1]:ds[0])+' мм',c.value,f('apps'))});
    if(!groups.length&&by['Применение'])row(axis&&eds.length?'Все диаметры':'Техника',by['Применение'],f('apps'));
    if(!f('apps').children.length){f('apps').hidden=true;f('apps-title').hidden=true}
    // все характеристики
    var all=f('chars');
    if(axis&&eds.length)row(axis,eds.map(function(e){return e[axis]}).sort(function(a,b){return num(a)-num(b)}).join('; '),all);
    chars.forEach(function(c){if(!hidden(c.title))row(c.title,c.value,all)});
    if(by['Сертификаты'])setText('cert',by['Сертификаты']);
    // фото: из каталога; если нет — остаются общие фото карточки
    var gal=arr(p.gallery).map(function(g){return g.img}).filter(Boolean);
    if(gal.length){
      var th=root.querySelector('.kp-gallery__thumbs');th.textContent='';
      gal.forEach(function(src,i){var b=el('button','kp-thumb'+(i?'':' is-active'));b.type='button';b.setAttribute('data-kp-photo',src);b.setAttribute('data-kp-cap',p.title);b.setAttribute('aria-label',p.title+', фото '+(i+1));if(!i)b.setAttribute('aria-current','true');var im=el('img');im.src=src;im.alt='';im.loading='lazy';b.appendChild(im);th.appendChild(b)});
      var m=root.querySelector('[data-kp-main]');m.src=gal[0];m.alt=p.title;th.hidden=gal.length<2;
    }
    setText('caption',p.title);var cap=root.querySelector('[data-kp-caption]');if(cap)cap.textContent=p.title;
    root.classList.remove('is-loading');window.dispatchEvent(new Event('resize'));
  }
  // смена диаметра — цена варианта
  root.addEventListener('click',function(e){var d=e.target.closest('[data-kp-d]');if(!d)return;setTimeout(function(){
    var pr=f('price'),on=d.getAttribute('aria-pressed')==='true',v=money(d.getAttribute('data-kp-price'));
    pr.textContent=on&&v?v:pr.getAttribute('data-kp-base')},0)});
  function get(path,params,cb,tries){
    var qs=Object.keys(params).map(function(k){return k+'='+encodeURIComponent(params[k])}).join('&');
    fetch('https://'+host+'/api/'+path+'/?'+qs).then(function(r){return r.json()}).then(function(d){
      if(d&&d.redirectto&&!tries){host=host.split('.').slice(0,-1).join('.')+'.'+d.redirectto;get(path,params,cb,1);return}
      cb(d)}).catch(function(){cb(null)})}
  if(!PID){fail('Товар не указан. Откройте карточку из каталога.');return}
  get('getproduct',{storepartuid:PART,recid:recid(),productuid:PID,c:Date.now()},function(d){
    var p=d&&(d.product||(d.uid?d:null));
    if(p){render(p);return}
    if(!PART){fail('Не удалось загрузить товар. Обновите страницу или вернитесь в каталог.');return}
    get('getproductslist',{storepartuid:PART,recid:recid(),c:Date.now(),getparts:'false',getoptions:'false',slice:1,size:500},function(l){
      var hit=l&&(l.products||[]).filter(function(x){return String(x.uid)===PID})[0];
      if(hit)render(hit);else fail('Товар не найден. Возможно, он снят с продажи.')})
  });
})();
'''
sub(r'</script>\n<!--krd-pops-->', LOADER + '</script>\n<!--krd-pops-->')
# в превью шаблон должен работать от GitHub Pages: свой номер блока не нужен
open(OUT, 'w', encoding='utf-8', newline='\n').write(html)
print('ok ->', os.path.relpath(OUT, ROOT))
