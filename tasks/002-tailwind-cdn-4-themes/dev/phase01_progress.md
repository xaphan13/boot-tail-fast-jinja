# Фаза 1: Tailwind CDN + JS-модель тем — DONE

- `_head.html`: Bootstrap CSS удалён; Tailwind Play CDN + инлайн-конфиг
  (семантические цвета на `--art-*`: page, surface, surface-2, ink, muted,
  line, accent, accent-strong, heading, codebg, codeink, ok, warn, danger,
  ring); инлайн-скрипт темы ставит `data-theme`; hljs-ссылки не тронуты.
- `_scripts.html`: Bootstrap bundle удалён.
- `scripts.js`: `applyTheme` ставит `data-theme`; добавлен `initNavToggle()`
  (`#nav-toggle` <-> `#nav-menu`, aria-expanded); комментарии приведены к
  новой модели.
- Checkpoint: приложение стартует. Роутов 42 (не 41 — доки устарели,
  Python-код заданием не трогается).
