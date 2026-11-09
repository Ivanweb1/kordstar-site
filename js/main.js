/* Кордстар — скрипты страницы.
   1–4: замена того, что делали скрипты Тильды (масштаб Zero-блоков, появление, меню, слайд команды).
   5–10: собственные скрипты страницы, перенесены без изменений логики. */

/* 1. Масштаб Zero-блоков: макет нарисован под ширины 1200/960/640/480/320 и растягивается на ширину окна */
(function () {
  // 480 пропускаем: ниже 640 везде телефонный макет (у Тильды макет 480–639 не доделан)
  var BREAKS = [1200, 960, 640, 320];
  function base() {
    for (var i = 0; i < BREAKS.length - 1; i++) {
      if (window.matchMedia('(min-width: ' + BREAKS[i] + 'px)').matches) return BREAKS[i];
    }
    return 320;
  }
  // настройка артборда для текущей ширины; если не задана — наследуется от более широкой
  function attr(ab, name, b) {
    var ALL = [1200, 960, 640, 480, 320];
    for (var i = ALL.indexOf(b); i >= 0; i--) {
      var v = ab.getAttribute('data-artboard-' + name + (i === 0 ? '' : '-res-' + ALL[i]));
      if (v !== null) return v;
    }
    return null;
  }
  function scale() {
    var w = document.documentElement.clientWidth;
    var b = base();
    // масштаб для собственных блоков (как у Zero-блоков от 1200px и шире)
    document.documentElement.style.setProperty('--kz', w >= 1200 ? w / 1200 : 1);
    document.querySelectorAll('.t396__artboard').forEach(function (ab) {
      var z = attr(ab, 'upscale', b) === 'window' ? w / b : 1;
      ab.style.setProperty('--zoom', z);
      var rec = ab.closest('.r');
      if (rec) rec.style.setProperty('--zoom', z);
      Array.prototype.forEach.call(ab.children, function (el) {
        if (el.classList.contains('t396__elem') || el.classList.contains('t396__group')) el.style.zoom = z === 1 ? '' : z;
      });
      var layers = [ab, ab.querySelector('.t396__carrier'), ab.querySelector('.t396__filter')];
      layers.forEach(function (el) { if (el) el.style.height = ''; });
      var h;
      if (attr(ab, 'heightmode', b) === 'hug') {
        ab.style.height = 'auto'; // высота по содержимому, как у Тильды
        h = ab.offsetHeight;
      } else {
        h = parseFloat(getComputedStyle(ab).height) * z;
      }
      layers.forEach(function (el) { if (el) el.style.height = h + 'px'; });
    });
  }
  // карточки с фиксированной высотой растут, если текст в них стал длиннее (после единой шкалы текста)
  var FIT = ['#rec3443016801 .tn-group[data-group-id="1789136628855000021"]'];
  function fit() {
    FIT.forEach(function (s) {
      var g = document.querySelector(s);
      if (!g || !g.offsetParent) return;
      var m = g.querySelector('.tn-molecule');
      [g, m].forEach(function (el) { if (el) el.style.minHeight = ''; });
      var z = parseFloat(g.style.zoom) || 1;
      var top = g.getBoundingClientRect().top, bottom = 0;
      g.querySelectorAll('.t396__elem').forEach(function (el) {
        bottom = Math.max(bottom, el.getBoundingClientRect().bottom);
      });
      var need = (bottom - top) / z + 25; // 25px — нижний отступ, как в оригинальной карточке
      [g, m].forEach(function (el) { if (el) el.style.minHeight = need + 'px'; });
    });
    // открытые ответы FAQ — высота по тексту (после загрузки шрифтов текст может стать длиннее)
    document.querySelectorAll('.qf-faq__item--open .qf-faq__answer').forEach(function (a) {
      a.style.maxHeight = a.scrollHeight + 'px';
    });
    // подписи под картинками на первом экране — ровно по центру своей карточки
    ['1788980163174000002', '1788980322607000008', '1788980291284000006', '1788980225687000004'].forEach(function (id) {
      var label = document.querySelector('#rec3719020401 .tn-elem[data-elem-id="' + id + '"]');
      var pill = label && label.closest('.t396__group');
      var card = pill && pill.parentElement.closest('.t396__group');
      if (!card || !pill.offsetParent) return;
      pill.style.left = (card.offsetWidth - pill.offsetWidth) / 2 + 'px';
    });
  }
  function update() { scale(); fit(); }
  update();
  if (document.fonts) document.fonts.ready.then(fit);
  var t;
  window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(update, 50); });
})();

/* 2. Появление элементов при прокрутке (fadein / fadeinup / … из настроек Тильды) */
(function () {
  // Первый экран: лёгкое появление снизу вверх — небольшой сдвиг, элементы по очереди сверху вниз
  var hero = document.querySelector('#rec3719020401 .t396__artboard');
  if (hero) {
    var items = Array.prototype.filter.call(hero.children, function (el) {
      return (el.classList.contains('t396__elem') || el.classList.contains('t396__group')) &&
        el.getAttribute('data-elem-type') !== 'shape'; // фоновые градиенты не трогаем
    });
    items.sort(function (a, b) { return a.getBoundingClientRect().top - b.getBoundingClientRect().top; });
    items.forEach(function (el, i) {
      el.classList.add('t-animate');
      el.setAttribute('data-animate-style', 'fadeinup');
      el.setAttribute('data-animate-distance', '24');
      el.setAttribute('data-animate-duration', '0.9');
      el.setAttribute('data-animate-delay', String(Math.min(i * 0.06, 0.6)));
    });
  }

  var els = document.querySelectorAll('.t396 .t-animate');
  function prep(el) {
    var style = el.getAttribute('data-animate-style') || 'fadein';
    var d = parseFloat(el.getAttribute('data-animate-distance')) || 0;
    var map = {
      fadeinup: 'translateY(' + d + 'px)', fadeindown: 'translateY(' + -d + 'px)',
      fadeinleft: 'translateX(' + d + 'px)', fadeinright: 'translateX(' + -d + 'px)',
      zoomin: 'scale(' + (parseFloat(el.getAttribute('data-animate-scale')) || 0.9) + ')',
      zoomout: 'scale(' + (parseFloat(el.getAttribute('data-animate-scale')) || 1.2) + ')'
    };
    el.classList.remove('t-animate_started');
    el.style.opacity = '0';
    el.style.transform = map[style] || 'none';
    el.style.transitionDuration = (parseFloat(el.getAttribute('data-animate-duration')) || 1) + 's';
    el.style.transitionDelay = (parseFloat(el.getAttribute('data-animate-delay')) || 0) + 's';
  }
  function show(el) {
    el.classList.add('t-animate_started');
    el.style.opacity = '1';
    el.style.transform = 'none';
  }
  if (!('IntersectionObserver' in window)) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { show(e.target); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -5% 0px' });
  els.forEach(function (el) { prep(el); io.observe(el); });
})();

/* 3. Меню: выпадающий список «О компании» и мобильный бургер */
(function () {
  var link = document.querySelector('a[href="#submenu:more"]');
  var tip = document.querySelector('.t794__tooltip-menu');
  if (link && tip) {
    tip.classList.add('t794__tooltip-menu_bottom');
    var hideT;
    function place() {
      var r = link.getBoundingClientRect();
      tip.style.position = 'fixed';
      tip.style.top = r.bottom + 28 + 'px'; // отступ под пунктом меню, как на исходной странице
      tip.style.left = r.left + r.width / 2 - tip.offsetWidth / 2 + 'px';
      var corner = tip.querySelector('.t794__tooltip-menu-corner');
      if (corner) { // уголок-стрелка по центру сверху
        corner.style.left = tip.offsetWidth / 2 - corner.offsetWidth / 2 + 'px';
        corner.style.top = -corner.offsetHeight / 2 + 'px';
      }
    }
    function open() { clearTimeout(hideT); tip.style.display = 'block'; place(); tip.classList.add('t794__tooltip-menu_show'); }
    function close() { hideT = setTimeout(function () { tip.classList.remove('t794__tooltip-menu_show'); tip.style.display = ''; }, 200); }
    link.addEventListener('click', function (e) { e.preventDefault(); tip.style.display === 'block' ? close() : open(); });
    [link, tip].forEach(function (el) {
      el.addEventListener('mouseenter', open);
      el.addEventListener('mouseleave', close);
    });
  }

  var burger = document.querySelector('.t-menu-burger');
  var menu = document.querySelector('.t-menu-popover__burgermenu');
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var opened = burger.getAttribute('aria-expanded') === 'true';
      var head = document.querySelector('#rec5382322501 .t-menu-popover__maincontainer');
      if (head) menu.style.setProperty('--menu-top', head.getBoundingClientRect().bottom + 'px');
      burger.setAttribute('aria-expanded', String(!opened));
      burger.classList.toggle('t-menu-burger_open', !opened); // бургер → крестик
      menu.classList.toggle('t-menu-popover__burgermenu_opened', !opened);
    });
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) burger.click();
    });
  }
})();

/* 4. Команда (десктоп): стрелки и клик по крайней карточке сдвигают ленту */
(function () {
  var group = document.querySelector('#rec3443016801 .Card-container');
  if (!group) return;
  var wrap = group.querySelector('.tn-atom__sbs-anim-wrapper');
  if (!wrap) return;
  wrap.style.transition = 'transform 0.8s ease-in-out';
  function go(state) {
    wrap.style.transform = state ? 'translateX(-540px)' : ''; // сдвиг из настроек анимации Тильды
  }
  var next = document.querySelector('#rec3443016801 .team-next');
  var prev = document.querySelector('#rec3443016801 .team-prev');
  var last = document.querySelector('#rec3443016801 [data-elem-id="1773906386994000004"]');
  if (next) next.addEventListener('click', function () { go(true); });
  if (last) last.addEventListener('click', function () { go(true); });
  if (prev) prev.addEventListener('click', function () { go(false); });
})();

/* 5. Сменяющийся подзаголовок первого экрана */
document.addEventListener("DOMContentLoaded", function() {
    const titles = [
        "производим и поставляем изделия из стальных канатов для спецтехники и лифтового оборудования",
        "грузоподъёмные механизмы и приспособления",
        "антидроновые сетки и защитные конструкции",
        "запасные части для спецтехники"
    ];
    
    let currentIndex = 0;
    
    // Находим все элементы с нашим классом (на случай автолейаутов и копий)
    const titleElements = document.querySelectorAll('.my-title .tn-atom'); 

    if (titleElements.length > 0) {
        // Задаем всем копиям плавность растворения (0.4 секунды)
        titleElements.forEach(el => {
            el.style.transition = "opacity 0.4s ease-in-out";
        });
        
        setInterval(() => {
            // 1. Уводим в полную прозрачность ВСЕ текстовые элементы
            titleElements.forEach(el => {
                el.style.opacity = '0';
            });
            
            // 2. Ждем 450 миллисекунд (пока текст ТОЧНО растворится и исчезнет)
            setTimeout(() => {
                currentIndex = (currentIndex + 1) % titles.length;
                
                titleElements.forEach(el => {
                    // Переписываем текст ТОЛЬКО в полной темноте
                    el.textContent = titles[currentIndex];
                    // 3. Плавно возвращаем видимость
                    el.style.opacity = '1';
                });
            }, 450); // Задержка чуть больше времени анимации, чтобы исключить наложение
            
        }, 2950); // Время чтения заголовка вместе с анимацией (~2.5 секунды чистого текста)
    }
});

/* 6. Фоновое видео первого экрана */
document.addEventListener("DOMContentLoaded", function() {
    function fixTildaVideos() {
        // Находим все MP4 видео внутри Zero Block
        const videos = document.querySelectorAll('.tn-atom video');
        
        videos.forEach(video => {
            // Убираем атрибут элементов управления
            video.removeAttribute('controls');
            video.controls = false;
            
            // Прописываем обязательные атрибуты для автоплея без багов
            video.setAttribute('autoplay', 'true');
            video.setAttribute('loop', 'true');
            video.setAttribute('muted', 'true');
            video.setAttribute('playsinline', 'true');
            video.setAttribute('webkit-playsinline', 'true');
            video.setAttribute('disablePictureInPicture', 'true');
            
            // Гарантируем, что звук выключен (иначе автоплей заблокируется)
            video.muted = true;
            
            // Принудительный запуск видео
            const playVideo = () => {
                if (video.paused) {
                    video.play().catch(err => {
                        console.log("Автоплей заблокирован браузером, пробуем снова...", err);
                    });
                }
            };

            playVideo();

            // Перезапуск, если видео случайно остановилось или из-за багов браузера
            video.addEventListener('pause', () => {
                video.play();
            });
            
            // Страховка для мобильных устройств: запускаем при первом взаимодействии с экраном
            ['click', 'touchstart', 'scroll'].forEach(eventType => {
                document.addEventListener(eventType, playVideo, { once: true });
            });
        });
    }

    // Запускаем сразу и на всякий случай через секунду для динамически погружаемых блоков
    fixTildaVideos();
    setTimeout(fixTildaVideos, 1000);
});

/* 7. «Как мы работаем?» — шаги */
(function () {
    var section = document.querySelector('.hwk');
    if (!section) return;

    var steps = parseInt(section.getAttribute('data-steps'), 10) || 3;
    var cards = section.querySelectorAll('.hwk__card');
    var fill = section.querySelector('.hwk__progress-fill');
    var track = section.querySelector('.hwk__track');
    var prevBtn = section.querySelector('.hwk__nav-btn--prev');
    var nextBtn = section.querySelector('.hwk__nav-btn--next');
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    section.style.setProperty('--steps', steps);

    var current = 0;

    function setStep(idx) {
      current = Math.max(0, Math.min(steps - 1, idx));

      cards.forEach(function (c, i) {
        c.classList.toggle('is-active', i === current);
      });

      if (fill) {
        var pct = steps > 1 ? (current / (steps - 1)) * 100 : 100;
        fill.style.width = pct + '%';
      }

      if (track) {
        track.style.transform = 'translate3d(0, ' + -(current * (100 / steps)) + '%, 0)';
      }

      if (prevBtn) prevBtn.disabled = current === 0;
      if (nextBtn) nextBtn.disabled = current === steps - 1;
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', function () {
        setStep(current - 1);
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        setStep(current + 1);
      });
    }

    setStep(0);
  })();

/* 8. «Наши работы» — появление карточек */
(function () {
      var root = document.querySelector('.wb-cases');
      if (!root) return;

      var reveals = root.querySelectorAll('.wb-cases__reveal');
      if (!('IntersectionObserver' in window)) {
        reveals.forEach(function (el) { el.classList.add('is-in'); });
        return;
      }

      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-in');
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

      reveals.forEach(function (el) { io.observe(el); });
    })();

/* 9. Слайдер команды (телефон) */
(function () {
    'use strict';

    var section =
      document.querySelector(
        '.vbg-section'
      );

    if (
      !section ||
      section.classList.contains(
        'vbg-booted'
      )
    ) {
      return;
    }

    var viewport =
      section.querySelector(
        '.vbg-viewport'
      );

    var currentElement =
      section.querySelector(
        '.vbg-counter__cur'
      );

    var totalElement =
      section.querySelector(
        '.vbg-counter__tot'
      );

    var progressFill =
      section.querySelector(
        '.vbg-progress__fill'
      );

    var previousButton =
      section.querySelector(
        '.vbg-btn--prev'
      );

    var nextButton =
      section.querySelector(
        '.vbg-btn--next'
      );

    if (
      !viewport ||
      !currentElement ||
      !totalElement ||
      !progressFill ||
      !previousButton ||
      !nextButton
    ) {
      return;
    }

    var ratio = 1.04;
    var sideWidth = 0.86;
    var sideHeight = 0.78;
    var gap = 0.05;
    var duration = 860;
    var chainDuration = 620;
    var dragStart = 6;
    var flick = 160;

    var cards = [];
    var photos = [];
    var count = 0;

    var position = 0;
    var target = 0;

    var cardWidth = 0;
    var cardHeight = 0;
    var mobileBioHeight = 0;
    var mobilePanelHeight = 0;
    var mobileExtraHeight = 0;

    var frame = null;
    var loopActive = false;
    var tween = null;

    var mutationTimer = null;
    var resizeTimer = null;
    var syncTimer = null;
    var lastCardCount = -1;
    var lastCardSignature = '';

    var reducedMotion =
      window.matchMedia(
        '(prefers-reduced-motion: reduce)'
      ).matches;

    var drag = {
      active: false,
      id: -1,
      startX: 0,
      startY: 0,
      positionStart: 0,
      moved: false,
      velocityX: 0,
      lastX: 0,
      lastTime: 0
    };

    function clamp(
      value,
      min,
      max
    ) {
      return value <
        min
          ? min
          : value >
            max
              ? max
              : value;
    }

    function lerp(
      from,
      to,
      amount
    ) {
      return from +
        (
          to -
          from
        ) *
        amount;
    }

    function mod(
      value,
      base
    ) {
      if (
        base <=
        0
      ) {
        return 0;
      }

      return (
        (
          value %
          base
        ) +
        base
      ) %
      base;
    }

    function easeInOut(
      value
    ) {
      return value <
        0.5
          ? 4 *
            value *
            value *
            value
          : 1 -
            Math.pow(
              -2 *
              value +
              2,
              3
            ) /
            2;
    }

    function easeOut(
      value
    ) {
      return 1 -
        Math.pow(
          1 -
          value,
          4
        );
    }

    function smoothstep(
      value
    ) {
      return value *
        value *
        (
          3 -
          2 *
          value
        );
    }

    function pad2(
      value
    ) {
      return String(
        value
      ).padStart(
        2,
        '0'
      );
    }

    function getCardSignature() {
      var currentCards =
        viewport.querySelectorAll(
          '.vbg-card'
        );

      var parts = [];

      for (
        var index = 0;
        index < currentCards.length;
        index++
      ) {
        var card =
          currentCards[index];

        var photo =
          card.querySelector(
            '.vbg-card__photo'
          );

        parts.push(
          String(index) +
          ':' +
          (
            photo
              ? photo.getAttribute('src') || ''
              : ''
          )
        );
      }

      return parts.join('|');
    }

    function syncCardIndexes() {
      cards.forEach(
        function (
          card,
          index
        ) {
          var indexElement =
            card.querySelector(
              '.vbg-panel__index'
            );

          if (indexElement) {
            indexElement.setAttribute(
              'data-index',
              pad2(
                index +
                1
              )
            );
          }
        }
      );
    }

    function refreshCards() {
      cards =
        Array.prototype.slice.call(
          viewport.querySelectorAll(
            '.vbg-card'
          )
        );

      photos =
        cards.map(
          function (card) {
            return card.querySelector(
              '.vbg-card__photo'
            );
          }
        );

      count =
        cards.length;

      syncCardIndexes();

      lastCardCount =
        count;

      lastCardSignature =
        getCardSignature();

      section.classList.toggle(
        'vbg-single',
        count <= 1
      );

      if (
        count <=
        0
      ) {
        position = 0;
        target = 0;
        tween = null;

        currentElement.textContent =
          '00';

        totalElement.textContent =
          '00';

        progressFill.style.width =
          '0%';

        viewport.style.height =
          '0px';

        return;
      }

      position =
        mod(
          Math.round(
            position
          ),
          count
        );

      target =
        position;

      currentElement.textContent =
        pad2(
          position +
          1
        );

      totalElement.textContent =
        pad2(
          count
        );

      progressFill.style.width =
        (
          100 /
          count
        ) +
        '%';

      measure();

      render(
        performance.now()
      );
    }

    function measureMobileContent() {
      if (
        viewport.offsetWidth >=
        768
      ) {
        mobileBioHeight = 0;
        mobilePanelHeight = 0;
        mobileExtraHeight = 0;

        section.style.removeProperty(
          '--vbg-mobile-bio-h'
        );

        section.style.removeProperty(
          '--vbg-mobile-panel-h'
        );

        return;
      }

      var maxBioHeight = 0;

      cards.forEach(
        function (card) {
          var bio =
            card.querySelector(
              '.vbg-panel__bio'
            );

          if (!bio) {
            return;
          }

          var previousWidth =
            card.style.width;

          card.style.width =
            cardWidth +
            'px';

          maxBioHeight =
            Math.max(
              maxBioHeight,
              bio.scrollHeight
            );

          card.style.width =
            previousWidth;
        }
      );

      mobileBioHeight =
        Math.ceil(
          maxBioHeight
        );

      mobilePanelHeight =
        Math.ceil(
          14 +
          mobileBioHeight +
          10 +
          27 +
          14
        );

      var baseHeight =
        cardHeight +
        70;

      var baselinePanelHeight =
        baseHeight *
        0.36;

      mobileExtraHeight =
        Math.max(
          0,
          mobilePanelHeight -
          baselinePanelHeight
        );

      section.style.setProperty(
        '--vbg-mobile-bio-h',
        mobileBioHeight +
        'px'
      );

      section.style.setProperty(
        '--vbg-mobile-panel-h',
        mobilePanelHeight +
        'px'
      );
    }

    function measure() {
      if (
        count <=
        0
      ) {
        return;
      }

      var viewportWidth =
        viewport.offsetWidth;

      if (
        viewportWidth <=
        0
      ) {
        return;
      }

      if (
        viewportWidth >=
        1200
      ) {
        cardWidth =
          clamp(
            0.30 *
            viewportWidth,
            270,
            400
          );
      }
      else if (
        viewportWidth >=
        768
      ) {
        cardWidth =
          clamp(
            0.38 *
            viewportWidth,
            240,
            330
          );
      }
      else {
        cardWidth =
          viewportWidth *
          0.68;
      }

      cardHeight =
        cardWidth *
        ratio;

      measureMobileContent();

      viewport.style.height =
        (
          cardHeight +
          70 +
          mobileExtraHeight
        ) +
        'px';
    }

    function render(
      now
    ) {
      if (
        count <=
        0
      ) {
        loopActive = false;

        return;
      }

      if (tween) {
        var raw =
          (
            now -
            tween.start
          ) /
          tween.duration;

        var amount =
          tween.ease(
            clamp(
              raw,
              0,
              1
            )
          );

        position =
          lerp(
            tween.from,
            tween.to,
            amount
          );

        if (
          raw >=
          1
        ) {
          position =
            tween.to;

          tween = null;
        }
      }

      var limit =
        count ===
        1
          ? 0
          : Math.min(
              2.9,
              Math.max(
                1,
                count /
                2 -
                0.1
              )
            );

      cards.forEach(
        function (
          card,
          index
        ) {
          var distance =
            mod(
              index -
              position,
              count
            );

          if (
            distance >
            count /
            2
          ) {
            distance -=
              count;
          }

          var absoluteDistance =
            Math.abs(
              distance
            );

          var opacity =
            absoluteDistance >
            limit
              ? 0
              : absoluteDistance >
                limit -
                0.5
                  ? clamp(
                      1 -
                      (
                        absoluteDistance -
                        (
                          limit -
                          0.5
                        )
                      ) *
                      2,
                      0,
                      1
                    )
                  : 1;

          var near =
            Math.min(
              absoluteDistance,
              1
            );

          var width =
            cardWidth *
            lerp(
              1,
              sideWidth,
              near
            );

          var height =
            cardHeight *
            lerp(
              1,
              sideHeight,
              near
            ) +
            70 +
            mobileExtraHeight;

          var sideCardWidth =
            cardWidth *
            sideWidth;

          var realGap =
            cardWidth *
            gap;

          var firstDistance =
            cardWidth /
            2 +
            realGap +
            sideCardWidth /
            2;

          var nextDistance =
            sideCardWidth +
            realGap;

          var offset =
            absoluteDistance <=
            1
              ? absoluteDistance *
                firstDistance
              : firstDistance +
                (
                  absoluteDistance -
                  1
                ) *
                nextDistance;

          var sign =
            distance <
            0
              ? -1
              : distance >
                0
                  ? 1
                  : 0;

          var translateX =
            sign *
            offset -
            width /
            2;

          var depth =
            100 -
            Math.round(
              absoluteDistance *
              10
            );

          var glass =
            smoothstep(
              clamp(
                1 -
                absoluteDistance,
                0,
                1
              )
            );

          var text =
            clamp(
              1 -
              absoluteDistance *
              1.7,
              0,
              1
            );

          card.setAttribute(
            'aria-hidden',
            absoluteDistance <
            0.5
              ? 'false'
              : 'true'
          );

          card.style.width =
            width +
            'px';

          card.style.height =
            height +
            'px';

          card.style.zIndex =
            String(
              depth
            );

          card.style.opacity =
            String(
              opacity
            );

          card.style.transform =
            'translate3d(' +
            translateX +
            'px,0,0)';

          card.style.setProperty(
            '--vbg-glass',
            String(
              glass
            )
          );

          card.style.setProperty(
            '--vbg-text',
            String(
              text
            )
          );

          if (
            photos[index]
          ) {
            photos[index].style.transform =
              'translate(-50%,-50%)';
          }
        }
      );

      var progress =
        mod(
          position,
          count
        );

      progressFill.style.transform =
        'translateX(' +
        progress *
        100 +
        '%)';

      if (
        !drag.active &&
        !tween
      ) {
        loopActive = false;
      }
      else {
        frame =
          requestAnimationFrame(
            render
          );
      }
    }

    function startLoop() {
      if (
        loopActive ||
        count <=
        0
      ) {
        return;
      }

      loopActive = true;

      frame =
        requestAnimationFrame(
          render
        );
    }

    function updateCounter(
      value
    ) {
      if (
        count <=
        0
      ) {
        return;
      }

      var index =
        mod(
          Math.round(
            value
          ),
          count
        );

      currentElement.textContent =
        pad2(
          index +
          1
        );

      totalElement.textContent =
        pad2(
          count
        );
    }

    function goTo(
      newTarget
    ) {
      if (
        count <=
        1
      ) {
        return;
      }

      var distance =
        Math.abs(
          newTarget -
          position
        );

      var ease;
      var tweenDuration;

      if (tween) {
        ease =
          easeOut;

        tweenDuration =
          chainDuration *
          clamp(
            0.6 +
            distance *
            0.4,
            0.6,
            1.6
          );
      }
      else {
        ease =
          reducedMotion
            ? function (
                value
              ) {
                return value <
                  1
                    ? 0
                    : 1;
              }
            : easeInOut;

        tweenDuration =
          duration *
          clamp(
            0.6 +
            distance *
            0.4,
            0.6,
            1.6
          );
      }

      if (
        reducedMotion
      ) {
        position =
          newTarget;

        target =
          newTarget;

        tween = null;

        updateCounter(
          newTarget
        );

        requestAnimationFrame(
          render
        );

        return;
      }

      target =
        newTarget;

      tween = {
        from: position,
        to: newTarget,
        start: performance.now(),
        duration: tweenDuration,
        ease: ease
      };

      updateCounter(
        newTarget
      );

      startLoop();
    }

    function stepBy(
      delta
    ) {
      if (
        count <=
        1
      ) {
        return;
      }

      var base =
        tween
          ? tween.to
          : Math.round(
              position
            );

      goTo(
        base +
        delta
      );
    }

    viewport.addEventListener(
      'pointerdown',
      function (event) {
        if (
          count <=
          1 ||
          event.button !==
          0
        ) {
          return;
        }

        drag.active = false;
        drag.moved = false;
        drag.id = event.pointerId;
        drag.startX = event.clientX;
        drag.startY = event.clientY;
        drag.positionStart =
          Math.round(
            position
          );

        drag.velocityX = 0;
        drag.lastX = event.clientX;
        drag.lastTime =
          performance.now();
      }
    );

    viewport.addEventListener(
      'pointermove',
      function (event) {
        if (
          event.pointerId !==
          drag.id ||
          count <=
          1
        ) {
          return;
        }

        var deltaX =
          event.clientX -
          drag.startX;

        var deltaY =
          event.clientY -
          drag.startY;

        if (
          !drag.active
        ) {
          if (
            Math.abs(
              deltaX
            ) <
            dragStart &&
            Math.abs(
              deltaY
            ) <
            dragStart
          ) {
            return;
          }

          if (
            Math.abs(
              deltaY
            ) >
            Math.abs(
              deltaX
            )
          ) {
            drag.id = -1;

            return;
          }

          drag.active = true;
          drag.moved = true;

          viewport.classList.add(
            'vbg-viewport--dragging'
          );

          viewport.setPointerCapture(
            event.pointerId
          );

          tween = null;

          drag.positionStart =
            position;
        }

        var now =
          performance.now();

        var timeDelta =
          now -
          drag.lastTime;

        if (
          timeDelta >
          0
        ) {
          var instantVelocity =
            (
              event.clientX -
              drag.lastX
            ) /
            timeDelta;

          drag.velocityX =
            drag.velocityX *
            0.7 +
            instantVelocity *
            0.3;
        }

        drag.lastX =
          event.clientX;

        drag.lastTime =
          now;

        var realGap =
          cardWidth *
          gap;

        var sideCardWidth =
          cardWidth *
          sideWidth;

        var firstDistance =
          cardWidth /
          2 +
          realGap +
          sideCardWidth /
          2;

        position =
          drag.positionStart -
          (
            event.clientX -
            drag.startX
          ) /
          firstDistance;

        startLoop();
      }
    );

    function endDrag(
      event
    ) {
      if (
        event.pointerId !==
        drag.id
      ) {
        return;
      }

      var wasDragging =
        drag.active;

      drag.active = false;
      drag.id = -1;

      viewport.classList.remove(
        'vbg-viewport--dragging'
      );

      try {
        viewport.releasePointerCapture(
          event.pointerId
        );
      }
      catch (error) {}

      if (
        !wasDragging
      ) {
        return;
      }

      var projected =
        position -
        drag.velocityX *
        flick;

      var rounded =
        Math.round(
          projected
        );

      rounded =
        clamp(
          rounded,
          drag.positionStart -
          2,
          drag.positionStart +
          2
        );

      var distance =
        Math.abs(
          rounded -
          position
        );

      target =
        rounded;

      tween = {
        from: position,
        to: rounded,
        start: performance.now(),
        duration:
          chainDuration *
          clamp(
            0.6 +
            distance *
            0.4,
            0.6,
            1.6
          ),
        ease: easeOut
      };

      updateCounter(
        rounded
      );

      startLoop();
    }

    viewport.addEventListener(
      'pointerup',
      endDrag
    );

    viewport.addEventListener(
      'pointercancel',
      endDrag
    );

    viewport.addEventListener(
      'dragstart',
      function (event) {
        event.preventDefault();
      }
    );

    viewport.addEventListener(
      'click',
      function (event) {
        if (
          drag.moved ||
          count <=
          1
        ) {
          drag.moved = false;

          return;
        }

        var card =
          event.target.closest(
            '.vbg-card'
          );

        if (
          !card ||
          !viewport.contains(
            card
          )
        ) {
          return;
        }

        var index =
          cards.indexOf(
            card
          );

        if (
          index <
          0
        ) {
          return;
        }

        var distance =
          mod(
            index -
            position,
            count
          );

        if (
          distance >
          count /
          2
        ) {
          distance -=
            count;
        }

        var offset =
          Math.round(
            distance
          );

        if (
          offset ===
          0
        ) {
          return;
        }

        var base =
          tween
            ? tween.to
            : Math.round(
                position
              );

        goTo(
          base +
          offset
        );
      }
    );

    previousButton.addEventListener(
      'click',
      function () {
        stepBy(
          -1
        );
      }
    );

    nextButton.addEventListener(
      'click',
      function () {
        stepBy(
          1
        );
      }
    );

    viewport.addEventListener(
      'keydown',
      function (event) {
        if (
          event.key ===
          'ArrowLeft'
        ) {
          event.preventDefault();

          stepBy(
            -1
          );
        }
        else if (
          event.key ===
          'ArrowRight'
        ) {
          event.preventDefault();

          stepBy(
            1
          );
        }
      }
    );

    var resizeObserver =
      new ResizeObserver(
        function () {
          clearTimeout(
            resizeTimer
          );

          resizeTimer =
            setTimeout(
              function () {
                measure();

                requestAnimationFrame(
                  render
                );
              },
              120
            );
        }
      );

    resizeObserver.observe(
      viewport
    );

    if (
      'MutationObserver' in window
    ) {
      var mutationObserver =
        new MutationObserver(
          function (records) {
            clearTimeout(
              mutationTimer
            );

            mutationTimer =
              setTimeout(
                function () {
                  var nextCount =
                    viewport.querySelectorAll(
                      '.vbg-card'
                    ).length;

                  var nextSignature =
                    getCardSignature();

                  var textChanged =
                    records.some(
                      function (record) {
                        if (
                          record.type ===
                          'characterData'
                        ) {
                          return true;
                        }

                        if (
                          record.type ===
                          'childList'
                        ) {
                          var target =
                            record.target &&
                            record.target.nodeType ===
                            1
                              ? record.target
                              : record.target.parentElement;

                          return !!(
                            target &&
                            target.closest &&
                            target.closest(
                              '.vbg-panel__bio'
                            )
                          );
                        }

                        return false;
                      }
                    );

                  if (
                    nextCount !==
                    lastCardCount ||
                    nextSignature !==
                    lastCardSignature
                  ) {
                    refreshCards();
                  }
                  else if (textChanged) {
                    measure();

                    requestAnimationFrame(
                      render
                    );
                  }
                },
                30
              );
          }
        );

      mutationObserver.observe(
        viewport,
        {
          childList: true,
          subtree: true,
          attributes: true,
          characterData: true,
          attributeFilter: [
            'src'
          ]
        }
      );
    }

    syncTimer =
      window.setInterval(
        function () {
          if (
            document.hidden
          ) {
            return;
          }

          var nextCount =
            viewport.querySelectorAll(
              '.vbg-card'
            ).length;

          var nextSignature =
            getCardSignature();

          if (
            nextCount !==
            lastCardCount ||
            nextSignature !==
            lastCardSignature
          ) {
            refreshCards();
          }
        },
        500
      );

    section._vbgDestroy =
      function () {
        if (
          frame
        ) {
          cancelAnimationFrame(
            frame
          );
        }

        clearTimeout(
          mutationTimer
        );

        clearTimeout(
          resizeTimer
        );

        if (
          syncTimer
        ) {
          clearInterval(
            syncTimer
          );
        }

        resizeObserver.disconnect();

        if (
          typeof mutationObserver !==
          'undefined'
        ) {
          mutationObserver.disconnect();
        }
      };

    section.classList.add(
      'vbg-booted',
      'vbg-ready'
    );

    refreshCards();

  })();

/* 10. FAQ — аккордеон */
(function () {
  var items = document.querySelectorAll('.qf-faq__item');

  function closeItem(item) {
    var btn = item.querySelector('.qf-faq__question');
    var ans = item.querySelector('.qf-faq__answer');
    if (!btn || !ans) return;
    btn.setAttribute('aria-expanded', 'false');
    ans.style.maxHeight = '0px';
    item.classList.remove('qf-faq__item--open');
  }

  function openItem(item) {
    var btn = item.querySelector('.qf-faq__question');
    var ans = item.querySelector('.qf-faq__answer');
    if (!btn || !ans) return;
    btn.setAttribute('aria-expanded', 'true');
    ans.style.maxHeight = ans.scrollHeight + 'px';
    item.classList.add('qf-faq__item--open');
  }

  items.forEach(function (item) {
    var btn = item.querySelector('.qf-faq__question');
    var ans = item.querySelector('.qf-faq__answer');
    if (!btn || !ans) return;

    if (item.classList.contains('qf-faq__item--open')) {
      ans.style.maxHeight = ans.scrollHeight + 'px';
    } else {
      ans.style.maxHeight = '0px';
    }

    btn.addEventListener('click', function () {
      var expanded = btn.getAttribute('aria-expanded') === 'true';
      if (expanded) {
        closeItem(item);
      } else {
        openItem(item);
      }
    });
  });

  window.addEventListener('resize', function () {
    document.querySelectorAll('.qf-faq__item--open').forEach(function (item) {
      var ans = item.querySelector('.qf-faq__answer');
      if (ans) ans.style.maxHeight = ans.scrollHeight + 'px';
    });
  });
})();

/* 11. Поп-апы заявок и отправка через форму Тильды.
   Кнопка с data-krd-popup="calc" открывает #krd-pop-calc. Своих приёмников у нас нет:
   заявка переписывается в обычную форму Тильды на этой же странице (блок с формой,
   у которого в настройках подключены почта / Telegram / CRM) и уходит её кнопкой.
   Блок-приёмник скрипт прячет сам — в Тильде его НЕ скрывать галочкой, иначе его нет в разметке.
   Схема та же, что на fulfil.pro (tilda/fx-runtime.js). */
(function () {
  var CFG = {
    donorSelector: 'form.js-form-proccess',
    submitTimeout: 300000, // капча Тильды может держать отправку несколько минут
    errorText: 'Не удалось отправить заявку. Позвоните нам: +7 (495) 150-92-22',
    phoneText: 'Проверьте номер телефона — нужно 10 цифр после +7',
    fillerEmail: 'no-reply@cordstar.ru'
  };
  var root = document.getElementById('krd-pops');
  if (!root) return;

  // В Тильде вайб-блок может лежать в обёртке с transform — fixed тогда ломается.
  // Переносим поп-апы в body; у обёртки класс vb-krd, поэтому стили блока к ним применяются.
  if (root.parentNode !== document.body) document.body.appendChild(root);

  var toast = root.querySelector('.krd-toast');
  var current = null;
  var lastFocus = null;
  var toastTimer;

  function showToast(text) {
    if (!toast) { alert(text); return; }
    toast.textContent = text;
    toast.classList.add('is-shown');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove('is-shown'); }, 6000);
  }

  /* ---------- открыть / закрыть ---------- */
  function lockScroll(on) {
    var html = document.documentElement;
    if (on) {
      var gap = window.innerWidth - html.clientWidth;
      html.style.overflow = 'hidden';
      if (gap > 0) document.body.style.paddingRight = gap + 'px';
    } else {
      html.style.overflow = '';
      document.body.style.paddingRight = '';
    }
  }

  function open(id) {
    var pop = document.getElementById('krd-pop-' + id);
    if (!pop) return;
    if (current) close(true);
    lastFocus = document.activeElement;
    pop.classList.remove('is-done');
    pop.classList.add('is-open');
    lockScroll(true);
    current = pop;
    requestAnimationFrame(function () {
      pop.classList.add('is-shown');
      var first = pop.querySelector('.krd-pop__body input:not([type="checkbox"]):not([type="radio"]), .krd-pop__body select, .krd-pop__body textarea');
      if (first && window.matchMedia('(min-width: 641px)').matches) first.focus({ preventScroll: true });
    });
  }

  function close(instant) {
    var pop = current;
    if (!pop) return;
    current = null;
    pop.classList.remove('is-shown');
    lockScroll(false);
    setTimeout(function () {
      pop.classList.remove('is-open');
      if (pop.classList.contains('is-done')) {
        pop.classList.remove('is-done');
        var form = pop.querySelector('form');
        if (form) form.reset();
      }
    }, instant === true ? 0 : 250);
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }

  document.querySelectorAll('[data-krd-popup]').forEach(function (el) {
    el.setAttribute('role', 'button');
    el.setAttribute('tabindex', '0');
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(el.getAttribute('data-krd-popup')); }
    });
  });
  document.addEventListener('click', function (e) {
    var trigger = e.target.closest && e.target.closest('[data-krd-popup]');
    if (trigger) { e.preventDefault(); open(trigger.getAttribute('data-krd-popup')); return; }
    if (current && e.target.closest && e.target.closest('[data-krd-close]')) close();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && current) close();
  });

  /* ---------- маска телефона ---------- */
  function phoneDigits(raw) {
    var d = String(raw || '').replace(/\D/g, '');
    while (d.length > 10 && (d.charAt(0) === '7' || d.charAt(0) === '8')) d = d.slice(1);
    return d.slice(0, 10);
  }
  function renderPhone(d) {
    if (!d) return '+7 ';
    var out = '+7 (' + d.slice(0, 3);
    if (d.length > 3) out += ') ' + d.slice(3, 6);
    if (d.length > 6) out += '-' + d.slice(6, 8);
    if (d.length > 8) out += '-' + d.slice(8, 10);
    return out;
  }
  root.addEventListener('input', function (e) {
    var f = e.target;
    if (f.name === 'phone') {
      var d = String(f.value).replace(/\D/g, '');
      if (d.charAt(0) === '7' || d.charAt(0) === '8') d = d.slice(1);
      f.value = renderPhone(d.slice(0, 10));
    }
    var field = f.closest('.krd-field');
    if (field) field.classList.remove('is-invalid');
  });
  root.addEventListener('focusin', function (e) {
    if (e.target.name === 'phone' && !e.target.value) e.target.value = '+7 ';
  });
  root.addEventListener('focusout', function (e) {
    if (e.target.name === 'phone' && !phoneDigits(e.target.value)) e.target.value = '';
  });

  /* ---------- сбор заявки ---------- */
  function collect(form) {
    var payload = { formName: form.getAttribute('data-krd-form') || 'Заявка с сайта' };
    var lines = [];
    var groups = {};
    form.querySelectorAll('input, textarea, select').forEach(function (f) {
      if (!f.name || f.type === 'submit') return;
      if (f.type === 'checkbox' || f.type === 'radio') {
        if (!f.checked) return;
        var box = f.closest('[data-label]');
        var label = box ? box.getAttribute('data-label') : f.name;
        if (!groups[label]) { groups[label] = []; lines.push({ group: label }); }
        groups[label].push(f.value);
        return;
      }
      var v = String(f.value || '').trim();
      if (!v) return;
      if (f.name === 'name' || f.name === 'phone' || f.name === 'email') { payload[f.name] = v; return; }
      lines.push({ text: (f.getAttribute('data-label') || f.name) + ': ' + v });
    });
    payload.details = lines.map(function (l) {
      return l.group ? l.group + ': ' + groups[l.group].join(', ') : l.text;
    }).join('\n');
    return payload;
  }

  function validate(form) {
    var bad = null;
    form.querySelectorAll('[required]').forEach(function (f) {
      var empty = !String(f.value || '').trim();
      if (f.name === 'phone') empty = phoneDigits(f.value).length !== 10;
      if (empty) {
        var field = f.closest('.krd-field');
        if (field) field.classList.add('is-invalid');
        if (!bad) bad = f;
      }
    });
    if (bad) {
      bad.focus();
      if (bad.name === 'phone' && phoneDigits(bad.value).length) showToast(CFG.phoneText);
      return false;
    }
    return true;
  }

  /* ---------- форма-приёмник Тильды ---------- */
  function findDonor() {
    var forms = document.querySelectorAll(CFG.donorSelector);
    for (var i = 0; i < forms.length; i++) {
      if (!forms[i].closest('.vb-krd')) return forms[i];
    }
    return null;
  }

  function hideDonor(donor) {
    // без этого Тильда покажет поверх своё окно «Спасибо»
    donor.removeAttribute('data-success-popup');
    donor.querySelectorAll('[data-success-popup]').forEach(function (n) { n.removeAttribute('data-success-popup'); });
    var rec = donor.closest('.r') || donor.closest('[id^="rec"]') || donor;
    if (rec.getAttribute('data-krd-hidden')) return;
    rec.setAttribute('data-krd-hidden', '1');
    rec.style.cssText += ';position:absolute!important;left:-9999px!important;top:0!important;' +
      'width:1px!important;height:1px!important;overflow:hidden!important;';
    rec.setAttribute('aria-hidden', 'true');
  }

  var ALIASES = { name: ['name', 'имя', 'fio'], phone: ['phone', 'tel', 'телефон'], email: ['email', 'mail', 'почта'] };
  function matchField(donor, key) {
    var inputs = donor.querySelectorAll('input, textarea');
    for (var i = 0; i < inputs.length; i++) {
      var f = inputs[i];
      if (f.type === 'hidden' || f.type === 'submit' || f.type === 'checkbox') continue;
      var hay = ((f.name || '') + ' ' + (f.placeholder || '')).toLowerCase();
      for (var j = 0; j < ALIASES[key].length; j++) if (hay.indexOf(ALIASES[key][j]) !== -1) return f;
    }
    return null;
  }

  function setHidden(donor, name, value) {
    var input = donor.querySelector('input[type="hidden"][name="' + name + '"]');
    if (!input) {
      input = document.createElement('input');
      input.type = 'hidden';
      input.name = name;
      donor.appendChild(input);
    }
    input.value = value == null ? '' : String(value);
  }

  function fire(f) {
    f.dispatchEvent(new Event('input', { bubbles: true }));
    f.dispatchEvent(new Event('change', { bubbles: true }));
  }

  // Поле «Телефон» Тильды — виджет с маской: видимое поле без кода страны и скрытое Phone
  // вида «+7 (926) 535-24-47» (Тильда проверяет длину ≥ 18 символов).
  function fillPhone(donor, value) {
    var sel = '.t-input-phonemask, [name^="tildaspec-phone-part"]:not([type="hidden"])';
    var visible = donor.querySelector(sel);
    if (!visible) return false;
    if (typeof window.t_form_phonemask_do === 'function' && visible.getAttribute('data-phonemask-iso') !== 'ru') {
      var rec = donor.closest('[id^="rec"]');
      var holder = donor.querySelector('[data-input-lid]');
      try {
        if (rec && holder) window.t_form_phonemask_do(rec.id.replace('rec', ''), holder.getAttribute('data-input-lid'), 'ru');
      } catch (e) { /* маска останется как есть */ }
      visible = donor.querySelector(sel) || visible;
    }
    var digits = phoneDigits(value);
    var template = visible.getAttribute('data-phonemask-without-code') || '(000) 000-00-00';
    var code = visible.getAttribute('data-phonemask-code') || '+7';
    var formatted = '', k = 0;
    for (var i = 0; i < template.length && k < digits.length; i++) {
      formatted += template.charAt(i) === '0' ? digits.charAt(k++) : template.charAt(i);
    }
    visible.value = formatted;
    visible.dispatchEvent(new Event('input', { bubbles: true }));
    visible.value = formatted; // маска могла переписать по-своему
    var result = donor.querySelector('.js-phonemask-result, input[type="hidden"][name="Phone"]');
    if (result) { result.value = code + ' ' + formatted; result.dispatchEvent(new Event('change', { bubbles: true })); }
    return true;
  }

  function fillDonor(donor, p) {
    var phoneDone = p.phone && fillPhone(donor, p.phone);
    ['name', 'phone', 'email'].forEach(function (key) {
      if (!p[key] || (key === 'phone' && phoneDone)) return;
      var f = matchField(donor, key);
      if (f) { f.value = p[key]; fire(f); }
      else setHidden(donor, key === 'name' ? 'Name' : key === 'phone' ? 'Phone' : 'Email', p[key]);
    });
    setHidden(donor, 'Форма', p.formName);
    setHidden(donor, 'Страница', document.title + ' — ' + location.pathname);
    setHidden(donor, 'Детали', p.details || '—');
    // свои обязательные поля приёмника (галка согласия, e-mail) посетитель не видит — закрываем их
    donor.querySelectorAll('[required], .js-tilda-rule').forEach(function (f) {
      if (f.type === 'checkbox' || f.type === 'radio') {
        if (!f.checked) { f.checked = true; f.dispatchEvent(new Event('change', { bubbles: true })); }
        return;
      }
      if (f.value) return;
      f.value = f.type === 'email' || /mail/i.test(f.name) ? CFG.fillerEmail : (p.formName || 'Заявка');
      fire(f);
    });
  }

  function tildaError(donor) {
    var box = donor.querySelector('.js-rule-error-all, .js-errorbox-all');
    return (box && box.textContent.trim()) || 'причина не указана';
  }

  // Тильда отправляет форму по клику на её кнопку; ход отправки виден в button.tildaSendingStatus:
  // «1» — идёт отправка, «0» — не прошла проверка полей.
  function submitViaTilda(donor, payload) {
    return new Promise(function (resolve, reject) {
      fillDonor(donor, payload);
      var button = donor.querySelector('[type="submit"]');
      if (!button) { console.error('[krd] В форме-приёмнике нет кнопки отправки', donor); reject(new Error('no-submit')); return; }
      var settled = false, timer;
      function guard(e) { if (e.target === donor) e.preventDefault(); }
      function cleanup() {
        donor.removeEventListener('tildaform:aftersuccess', ok);
        donor.removeEventListener('tildaform:aftererror', err);
        document.removeEventListener('submit', guard, true);
        clearTimeout(timer);
      }
      function ok() { if (settled) return; settled = true; cleanup(); resolve(); }
      function fail(msg) {
        if (settled) return;
        settled = true;
        cleanup();
        window.KRD_LAST_ERROR = msg;
        console.error('[krd] ' + msg, donor);
        reject(new Error(msg));
      }
      function err() { fail('Тильда сообщила об ошибке: ' + tildaError(donor)); }
      document.addEventListener('submit', guard, true);
      donor.addEventListener('tildaform:aftersuccess', ok);
      donor.addEventListener('tildaform:aftererror', err);
      donor.removeAttribute('data-success-popup');
      button.tildaSendingStatus = '';
      button.click();
      setTimeout(function () {
        if (settled) return;
        var st = button.tildaSendingStatus;
        if (st === '1') return; // отправка идёт, ждём событие
        if (st === '0') { fail('Тильда не приняла поля: ' + tildaError(donor)); return; }
        fail('Форма-приёмник есть, но Тильда её не обслуживает — проверьте, что страница опубликована и у формы подключён приёмник данных.');
      }, 60);
      timer = setTimeout(function () {
        fail('Тильда не подтвердила отправку за ' + (CFG.submitTimeout / 1000) + ' с');
      }, CFG.submitTimeout);
    });
  }

  function isDemoHost() {
    return location.protocol === 'file:' || /^(localhost|127\.0\.0\.1)$|\.github\.io$/.test(location.hostname);
  }

  function send(payload) {
    var donor = findDonor();
    if (donor) { hideDonor(donor); return submitViaTilda(donor, payload); }
    if (isDemoHost()) {
      console.info('[krd] Демо: формы Тильды на странице нет, заявка не отправлена', payload);
      return new Promise(function (r) { setTimeout(r, 600); });
    }
    console.error('[krd] Заявка никуда не ушла: добавьте на страницу блок с формой Тильды и подключите приёмник данных.', payload);
    return Promise.reject(new Error('no-donor'));
  }

  // приёмник прячем сразу, а не при первой заявке
  var early = findDonor();
  if (early) hideDonor(early);
  else document.addEventListener('DOMContentLoaded', function () { var d = findDonor(); if (d) hideDonor(d); });

  root.querySelectorAll('form[data-krd-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (form.getAttribute('data-krd-busy') === '1') return;
      if (!validate(form)) return;
      var button = form.querySelector('[type="submit"]');
      var label = button ? button.textContent : '';
      form.setAttribute('data-krd-busy', '1');
      if (button) { button.disabled = true; button.textContent = 'Отправляем…'; }
      send(collect(form)).then(function () {
        var pop = form.closest('.krd-pop');
        if (pop) pop.classList.add('is-done');
        form.reset();
      }).catch(function () {
        showToast(CFG.errorText);
      }).then(function () {
        form.removeAttribute('data-krd-busy');
        if (button) { button.disabled = false; button.textContent = label; }
      });
    });
  });

  window.KRD_POPUP = { open: open, close: close };
})();
