# Фаза 4: Флеш, макрос форм, страницы аккаунта — DONE

- `_flash_msg.html`: класс `flash flash-<category>` (категории кода:
  success, danger, info, warning, message — все имеют стили в base.css).
- `_form_macro.html`: контракт данных прежний; поля rounded-xl, ошибка —
  border-danger + список text-danger; file_field с file:-вариантами.
  Параметр size (form-control-lg) удалён — вызывающие его не передавали.
- `login.html`, `register.html`: карточка max-w-md rounded-2xl shadow,
  чекбокс с accent-цветом, кнопка btn-grad rounded-xl.
- `account.html`: аватар h-20 w-20 с градиентным кольцом, секция
  «Данные аккаунта» uppercase-заголовком.
- `about.html`: карточка с текстом.
- Checkpoint: POST /register с ошибками -> 200, ошибки видны (text-danger),
  invalid-feedback/is-invalid = 0; POST /login неверный пароль -> flash-danger.
