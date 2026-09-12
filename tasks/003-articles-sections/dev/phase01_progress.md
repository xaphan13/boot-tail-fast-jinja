# Фаза 1 — Рекурсивный скан и хелперы раздела

Зона: `fastapi-application/md_articles/schema_art.py`

## План
1. Заменить тело `scan_content_art()` на рекурсивный `rglob("*")` с POSIX-путями
   относительно `content_art/`, фильтр `is_file()` + `.md/.markdown` (case-insensitive),
   отсортированный `sorted()`.
2. Добавить `get_section(file_name: str) -> str` через `Path(file_name).parts`.
3. Добавить `list_sections() -> list[str]` по зарегистрированным статьям.
4. `ArticleLang`, `_FIELDS_FOR_YAML`, `save_articles` — не трогать.

## Журнал
- 2026-09-11: старт фазы, прочитан контракт фазы 1 и целевой файл.
- 2026-09-11: `md_articles/schema_art.py` — `scan_content_art` переведён на рекурсивный
  `rglob("*")` с POSIX-путями; добавлены `get_section` и `list_sections`.
  Проверки: ruff — All checks passed; импорт + вызовы функций — 80 файлов,
  section первого файла `AI инструменты`, 10 непустых секций.
  Сырой вывод: `dev/phase01_scan.txt`. Статус: GREEN.