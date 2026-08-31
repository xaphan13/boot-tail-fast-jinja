# Фаза 3: Каркас (layout, шапка, сайдбар, футер, селекторы) — DONE

- `layout.html`: `<html data-theme="dark">`; flex-каркас, fixed-шапка,
  main pt-24, сайдбар md:w-56, футер mt-auto.
- `_header.html`: градиентная шапка `.site-header-grad`, бренд `.brand-text`
  (белый -> акцент темы), гамбургер `#nav-toggle` (md:hidden, svg), меню
  `#nav-menu` (hidden md:flex), ссылки-пилюли на белых тонах (шапка тёмная
  во всех темах), оба селектора в обеих ветках.
- `_theme_select.html` / `_hljs_theme_select.html`: id и option-ы прежние,
  классы Tailwind (bg-surface-2, rounded-lg, focus:ring-ring).
- `_sidebar.html`: пилюли с hover-сдвигом.
- `_footer_macro.html`: панель bg-surface, центрированные ссылки.
- Checkpoint: /login содержит data-theme, cdn.tailwindcss.com,
  id="theme-select", id="hljs-theme-select"; data-bs-theme=0, navbar=0.
