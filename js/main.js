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
  scale();
  var t;
  window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(scale, 50); });
})();

/* 2. Появление элементов при прокрутке (fadein / fadeinup / … из настроек Тильды) */
(function () {
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
