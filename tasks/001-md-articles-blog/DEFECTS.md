# DEFECTS.md

## DEF-001: Формы на /art_manage не содержат csrf_token — POST всегда возвращает 403

- Status: CLOSED
- Severity: HIGH
- Found by: qa
- Task: Порт блога flask-blog-1 на FastAPI + Jinja

Steps to reproduce:
1. cd fastapi-application && ../.venv/bin/uvicorn main:main_app --port 8000
2. Зарегистрируйтесь/войдите (POST /login с csrf_token, email=e2e_user@example.com, password=QaPass123)
3. GET /art_manage — страница управления статьями, 200, показывает список статей с формами
4. Проверьте HTML форм: каждая форма содержит `<input type="hidden" name="file_name">`, `<input name="title">`, `<input name="author">`, `<input name="lang">`, `<button type="submit">`, но НЕ содержит `<input type="hidden" name="csrf_token" value="...">`
5. Попробуйте отправить форму (POST /art_manage/meta с file_name=FastAPI_CodeReview.docx.md&author=Max&lang=Python&title=FastAPI_CodeReview.docx)

Expected: 307 redirect с flash "Обновлена запись для ..."
Actual: 403 "Доступ запрещён (403)" — серверная CSRF-проверка отклоняет запрос без csrf_token, но формы не предоставляют этот токен
Screenshot: tasks/current/screenshots/def-001.png (опционально)

History:
- qa: opened (2026-08-31, found during criterion 9 testing; server-side CSRF validation is correct — it properly rejects requests without token — but the HTML forms in art_manage template are missing the csrf_token hidden input, making the feature unusable from the browser)
- оркестратор: передано frontend-dev
- frontend-dev: ИСПРАВЛЕНО — в art_manage.html в каждую из трёх POST-форм добавлена первой строкой `<input type="hidden" name="csrf_token" value="{{ csrf_token }}">` (строки 40, 87, 96: inline-форма «Все статьи», форма «Добавить все», формы unassigned_files); дизайн и остальная разметка не тронуты
- оркестратор: статус FIX-READY (2026-08-31)
- qa: CLOSED (2026-08-31, перетест пройден: csrf в формах, POST meta 307 + flash, POST add_all 307 + flash «Нет новых файлов», реестр не повреждён — e2e/batch6_retest_def001.txt)
