# Фаза 2: base.css — 4 палитры + типографика — DONE

- Файл переписан целиком.
- 4 блока `[data-theme=...]`: dark (графит/голубой), light (тёплый бумажный),
  midnight (сине-фиолетовый), aurora (изумрудный). В каждом полный набор
  `--art-*` (20 переменных): page, surface, surface-2, ink, muted, line,
  accent, accent-strong, heading, header-from/via/to, grad, ring, brand,
  code-bg, code-ink, ok, warn, danger.
- Базовая типографика (body/a/h1-h6) с префиксом `body` против Tailwind
  preflight; типографика `.art-body` (p, h2-h3, списки, blockquote, table,
  pre/code, ссылки).
- Хелперы: `.site-header-grad`, `.btn-grad`, `.grad-text`, `.brand-text`,
  `.badge` + `badge-accent/ok/warn/danger`, `.flash` + 5 категорий,
  `.hljs-theme-select`, скругления pre/.hljs/inline-code.
- color-mix() для прозрачных тинтов (современные браузеры).
- Checkpoint: CSS отдаётся 200, 8 вхождений `[data-theme=`, скобки 44/44.
