# Фаза 5: Страницы статей — DONE

- `art_home.html`: карточки статей (rounded-2xl, hover: border-accent,
  -translate-y-0.5, shadow-lg), бейджи .badge / .badge-accent.
- `art_author.html`: карточка статьи, шапка с бейджами, тело .art-body;
  понижение h1->h2 в теле сохранено (на странице ровно один h1).
- `art_manage.html`: три секции-карточки с градиентной линией под h2,
  таблица реестра (rounded-xl контейнер, thead bg-surface-2, divide-y,
  hover строк), inline-формы на сетке md:grid-cols-12, статусы
  badge-ok/warn/danger, списки файлов — карточки с hover:border-accent.
  Имена полей, роуты, csrf_token не менялись. Bootstrap-класс ms-2
  заменён на Tailwind ml-2.
- Checkpoint: /art_home 200 (5 карточек); статья 200; /art_manage без
  авторизации 307 -> /login?next=/art_manage.
