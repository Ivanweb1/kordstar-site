# Иконки для карточки 1СК

Иконки на сайте объёмные: стеклянные, светло-бирюзовые, на бледно-мятной квадратной плашке со скруглёнными углами.
В `refs/` лежат образцы с главной. Приложите их к генерации как референсы стиля (2–3 штуки, лучше всего 1, 2 и 3).

## Что нужно сгенерировать

Готовые картинки положите в `new/` с такими именами (PNG, квадрат, от 512×512):

| Файл | Где стоит на карточке | Сейчас временно |
|---|---|---|
| `new/delivery.png` | «Доставка по России» (блок «Почему Кордстар») | кран |
| `new/docs.png` | вкладка «Качество и сертификация» → «Документация» | звенья цепи |
| `new/warranty.png` | вкладка «Гарантия» → «Условия гарантии» | звенья цепи |

## Промпты

Общая часть (одинаковая для всех трёх, чтобы стиль совпадал):

> glossy translucent glass material in light aqua-teal (#7fd3d6 to #a9e4e6) with soft white highlights, isometric 3/4 view, centered on a pale mint rounded square tile (#eef7f8) with soft rounded corners, soft studio lighting, subtle shadow, minimal, clean, no text, 1:1, 512x512. Match the style of the attached reference icons exactly.

**delivery.png**

```
3D icon of a small cargo delivery truck, glossy translucent glass material in light aqua-teal (#7fd3d6 to #a9e4e6) with soft white highlights, isometric 3/4 view, centered on a pale mint rounded square tile (#eef7f8) with soft rounded corners, soft studio lighting, subtle shadow, minimal, clean, no text, 1:1, 512x512. Match the style of the attached reference icons exactly.
```

**docs.png**

```
3D icon of a document sheet with a small certificate seal ribbon, glossy translucent glass material in light aqua-teal (#7fd3d6 to #a9e4e6) with soft white highlights, isometric 3/4 view, centered on a pale mint rounded square tile (#eef7f8) with soft rounded corners, soft studio lighting, subtle shadow, minimal, clean, no text, 1:1, 512x512. Match the style of the attached reference icons exactly.
```

**warranty.png**

```
3D icon of a shield with a check mark, glossy translucent glass material in light aqua-teal (#7fd3d6 to #a9e4e6) with soft white highlights, isometric 3/4 view, centered on a pale mint rounded square tile (#eef7f8) with soft rounded corners, soft studio lighting, subtle shadow, minimal, clean, no text, 1:1, 512x512. Match the style of the attached reference icons exactly.
```

Перевести в `img/icon-*.webp` (обрезка под пропорции иконок с главной, 144×144, прозрачные углы): `python tools/icons_prep.py`. Сейчас стоят в карточке 1СК: доставка, документация, гарантия.
