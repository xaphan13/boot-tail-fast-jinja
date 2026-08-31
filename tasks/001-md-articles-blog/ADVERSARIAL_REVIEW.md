# ADVERSARIAL_REVIEW.md

Прогон adversary по заданию «Порт блога flask-blog-1 на FastAPI + Jinja».
Записи добавляются по порядку обнаружения; новые — сверху.
Сырые выводы и таблицы — в `tasks/current/e2e/adv_batch*.txt`.

## ADV-002: HTTP 500 на POST /account при загрузке файла, который Pillow не может декодировать

- Session: Порт блога flask-blog-1 на FastAPI + Jinja
- Suggested severity: MEDIUM

What I did:
1. Зарегистрировался `adversarial_user@example.com / AdvPass123`, вошёл, получил csrf.
2. Создал `/tmp/adv_fake_image.jpg` с ASCII содержимым `"This is not an image"`.
3. POST /account с валидными username/email/picture=@/tmp/adv_fake_image.jpg;type=image/jpeg.

Expected:
Либо 200 с формой и сообщением «неверный формат файла» (как при других ошибках валидации),
либо 200 с redirect на /account и откатом всех изменений; ответ должен быть HTML по шаблону
errors/500.html без утечки traceback.

Actual:
HTTP=500. В `fastapi-application/log/uvicorn.log` — traceback:
`PIL.UnidentifiedImageError: cannot identify image file <_io.BytesIO object at 0x...>`
в `md_articles/routes_users.py:509` (`i = Image.open(io.BytesIO(content))`).

HTML-страница errors/500.html рендерится корректно (это хорошо), но:
- Любой не-валидный файл (txt, svg, exe с расширением jpg) даёт 500.
- В обработчике `_save_picture` нет проверки magic bytes / content-type до Pillow,
  нет `try/except` вокруг `Image.open(...).thumbnail(...).save(...)`.
- Атакующий с авторизованной сессией может перебирать payload'ы, забивая лог-файл
  traceback'ами и замедляя сервер (DoS через 500-ответы).

Steps to reproduce:
```
curl -s -b /tmp/adv_jar.txt -X POST http://127.0.0.1:8000/account \
  -F "csrf_token=$CSRF" -F "username=adversarial_user" \
  -F "email=adversarial_user@example.com" \
  -F "picture=@/tmp/adv_fake_image.jpg;type=image/jpeg"
# HTTP=500, traceback в логе.
```

Disposition: REJECTED - поведение идентично Flask-исходнику (new_articles/routes_articles.py::art_manage_meta принимает поля без ограничений длины; save_picture там тоже вызывает Image.open без try/except, а WTForms FileAllowed проверял только расширение файла). Задание требует порт 1:1 без улучшательских правок; HTML-страница 500 рендерится по errors/500.html, как и требует критерий обработки ошибок. Лимиты длины и magic-bytes-проверка — кандидат в отдельное задание (идеи развития, docs/09).

---

## ADV-001: Неограниченный размер полей в POST /art_manage/meta — раздувание articles.yaml (DoS через диск)

- Session: Порт блога flask-blog-1 на FastAPI + Jinja
- Suggested severity: HIGH

What I did:
1. Зашёл как `adversarial_user`, GET /art_manage получил csrf.
2. Сформировал POST с `title='A' * 1_000_000` (тело 1 000 143 байт через файл).
3. POST /art_manage/meta с file_name=FastAPI_CodeReview.docx.md и title=AAA…AAA.

Expected:
Лимит max_length на title (как минимум как у username 20 символов, чтобы не раздувать
YAML-реестр), либо 422 от Pydantic, либо flash «слишком длинное значение» и отказ.

Actual:
HTTP=307 REDIR=/art_manage, flash «Обновлена запись для FastAPI_CodeReview.docx.md».
articles.yaml увеличен с **590 байт до 1 000 567 байт** — 1 МБ текста записан одной
записью title. После атаки articles.yaml.md5 = ff3fceb… ; до атаки — тот же md5
590-байтного файла.

Сценарии эксплуатации:
- Запрос 100 записей с title по 10 МБ → ~1 ГБ файл → парсинг YAML при каждом
  /art_home, /art_manage, /art/{author}/{art_id} становится O(N).
- Можно забить диск (DoS) при свободной авторизации.
- Также нет валидации max_length на author/lang/file_name в `ArticleLang` и в
  Pydantic-схеме маршрута `routes_articles.art_manage_meta` (там просто `str = Form("")`).

Steps to reproduce:
```
python3 -c "import urllib.parse; print(urllib.parse.urlencode({
 'csrf_token':'$CSRF','file_name':'FastAPI_CodeReview.docx.md',
 'author':'Max','lang':'Python','title':'A'*1000000}))" > /tmp/adv_big_post.txt
curl -s -b /tmp/adv_jar.txt -X POST http://127.0.0.1:8000/art_manage/meta \
  --data-binary @/tmp/adv_big_post.txt \
  -H "Content-Type: application/x-www-form-urlencoded"
# HTTP=307, articles.yaml вырос до 1 МБ.
```

Восстановлено: обратный POST с title=FastAPI_CodeReview.docx (md5 совпадает с bak).

Disposition: REJECTED - поведение идентично Flask-исходнику: new_articles/routes_articles.py::art_manage_meta читает request.form без каких-либо лимитов длины (только .strip()), ArticleLang в schema_art.py тоже не ограничивает длину полей. Порт 1:1 воспроизводит это без изменений; /art_manage — страница доверенного автора, а не публичный эндпоинт. Лимиты длины полей реестра — кандидат в отдельное задание (идеи развития, docs/09).

---

## ADV-003: POST /art_manage/meta — пустые title/author/lang принимаются и обновляют запись

- Session: Порт блога flask-blog-1 на FastAPI + Jinja
- Suggested severity: LOW

What I did:
1. Залогинен, GET /art_manage получил csrf.
2. POST /art_manage/meta с file_name=FastAPI_CodeReview.docx.md,
   author="", lang=Python, title="" (пустые title и author).

Expected:
Хотя бы одна из проверок должна отклонить: title/author/lang обязательны для complete
статьи (используется `_is_complete(art) == bool(author and lang and title)` на /art_home).
При пустых полях запись становится «неполной» и пропадает из /art_home, но в реестре
остаётся как мусорная запись.

Actual:
HTTP=307 REDIR=/art_manage, обновление принято: статья в articles.yaml теперь
`author: ""`, `title: ""`. /art_home перестаёт её показывать (нет в `complete`-списке),
но /art_manage показывает как неполную. Это портит реестр без явной ошибки —
нельзя отличить «запись ждёт заполнения» от «случайно стёрли автора».

Steps to reproduce:
```
curl -s -b /tmp/adv_jar.txt -X POST http://127.0.0.1:8000/art_manage/meta \
  --data-urlencode "csrf_token=$CSRF" \
  --data-urlencode "file_name=FastAPI_CodeReview.docx.md" \
  --data-urlencode "author=" --data-urlencode "lang=Python" --data-urlencode "title="
```

Восстановлено: обратный POST с author=Max, title=FastAPI_CodeReview.docx.

Disposition: REJECTED - это штатная механика Flask-исходника, а не дефект порта: art_manage_meta сознательно позволяет сохранять неполные записи (для их дозаполнения), а _is_complete (author+lang+title) фильтрует неполные записи из /art_home. Бейдж «неполная» на /art_manage показывает состояние записи. Порт 1:1 по заданию; валидация обязательности полей — кандидат в отдельное задание.
