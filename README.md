# Web Hero — Modular Genesis

Отдельная Blender-сцена для фонового hero сайта. Не связана с `grok cli test`.

Тема собрана под твои проекты: **Modular Genesis**, VCV Rack, Ableton, еврорэк, audiovisual lab.

## Живой пайплайн (то, что нужно)

```
Blender  →  hero.glb  →  Three.js  →  GSAP
```

Не видео. Камера, парение и параллакс мыши крутит GSAP.

```bat
cd web
start.bat
```

Открой http://127.0.0.1:8765

| Файл | Зачем |
|---|---|
| `web/hero.glb` | Сцена из Blender |
| `web/main.js` | Three.js + GSAP |
| `export_glb.py` | Переэкспорт GLB |

## Что внутри

| Файл | Зачем |
|---|---|
| `hero_loop.blend` | Сцена, 8 секунд, кадры 1–192 |
| `create_hero.py` | Полная пересборка с нуля |
| `renders/still.png` | Кадр для постера |
| `renders/loop.mp4` | Зацикленное видео для сайта |
| `web/index.html` | Превью, как это сидит на лендинге |

## Рендер только на видеокарте

Скрипт включает **OPTIX / RTX 3050** и выключает CPU в Cycles. EEVEE и так идёт на GPU.

Перед любым рендером:

```bat
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" "hero_loop.blend" --background --python lock_gpu.py
```

## Пересобрать

```bat
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python create_hero.py
```

Луп (дольше):

```bat
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python create_hero.py -- --anim
```

Открыть превью: `web/index.html`.
