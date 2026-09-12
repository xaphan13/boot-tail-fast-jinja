# ==============================================================================
# +++++++++++++++++++++++++++++ routes_articles ++++++++++++++++++++++++++++++++
# -------------------- /art_home /art/... /art_manage/* ------------------------
# ------------------------------------------------------------------------------
import os
import time
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from config_log import logF
from md_articles.web_utils import flash, render_template, require_login, validate_csrf
from md_articles.schema_art import (
    ArticleLang,
    get_art,
    get_articles,
    get_path_dir,
    get_registry_error,
    render_article,
    save_articles,
    scan_content_art,
    get_section,
    list_sections,
)


DEFAULT_AUTHOR = "NoName"

router_articles = APIRouter(
    tags=["blog articles"],
)


# ==============================================================================
# +++++++++++++++++++++++++++++++ art_home +++++++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@router_articles.get("/art_home", name="art_main.art_home")
async def art_home(request: Request):
    title_list = [
        art.model_dump(exclude={"content"}) for art in get_articles() if _is_complete(art)
    ]
    logF.info(f"new_art : '/art_home' = {title_list}")

    return render_template(
        "new_art/art_home.html",
        {"request": request, "title_list": title_list},
    )


# ==============================================================================
# +++++++++++++++++++++++++++++++ art_section ++++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@router_articles.get("/art_section/{section}", name="art_main.art_section")
async def art_section(request: Request, section: str):
    if section not in list_sections():
        raise HTTPException(status_code=404)
    title_list = [art.model_dump(exclude={"content"}) for art in get_articles() if _is_complete(art) and get_section(art.file_name) == section]
    return render_template(
        "new_art/art_home.html",
        {"request": request, "title_list": title_list, "section": section},
    )


# ==============================================================================
# +++++++++++++++++++++++++++++++ art_author +++++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@router_articles.get("/art/{author}/{art_id}", name="art_main.art_author")
async def art_author(request: Request, author: str, art_id: int):
    logF.info(f"art_author : '/art/<string:author>/<int:art_id>' = {author} - {art_id}")

    art = get_art(art_id)
    if art is None:
        raise HTTPException(status_code=404)

    if not _is_complete(art):
        raise HTTPException(status_code=404)

    content_dir = get_path_dir()
    if not os.path.exists(content_dir / art.file_name):
        raise HTTPException(status_code=404)

    content = render_article(art.file_name, content_dir)
    art_for_template = art.model_copy(update={"content": content})

    return render_template(
        "new_art/art_author.html",
        {"request": request, "lang": art_for_template.lang, "art": art_for_template},
    )


# ==============================================================================
# +++++++++++++++++++++++++++++++ art_manage +++++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@router_articles.get("/art_manage", name="art_main.art_manage")
async def art_manage(request: Request, _user=Depends(require_login)):
    articles = get_articles()
    disk_files = set(scan_content_art())
    registered_files = {art.file_name for art in articles}

    unassigned_files = [name for name in disk_files if name not in registered_files]

    articles_context = [
        {
            "art_id": art.art_id,
            "file_name": art.file_name,
            "title": art.title,
            "author": art.author,
            "lang": art.lang,
            "complete": _is_complete(art),
            "file_exists": art.file_name in disk_files,
        }
        for art in articles
    ]

    missing_entries = [
        {
            "art_id": art.art_id,
            "file_name": art.file_name,
            "title": art.title,
            "author": art.author,
            "lang": art.lang,
            "complete": _is_complete(art),
            "file_exists": False,
        }
        for art in articles
        if art.file_name not in disk_files
    ]

    return render_template(
        "new_art/art_manage.html",
        {
            "request": request,
            "articles": articles_context,
            "unassigned_files": unassigned_files,
            "missing_entries": missing_entries,
            "yaml_error": get_registry_error(),
            "title": "Управление статьями",
        },
    )


# ==============================================================================
# ++++++++++++++++++++++++++++ art_manage_add_all +++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@router_articles.post("/art_manage/add_all", name="art_main.art_manage_add_all")
async def art_manage_add_all(request: Request, _user=Depends(require_login)):
    await validate_csrf(request)

    disk_files = sorted(scan_content_art())
    if not disk_files:
        flash(request, "Нет новых файлов для добавления", "info")
        return RedirectResponse("/art_manage", status_code=303)

    articles = list(get_articles())
    registry_by_file = {art.file_name: art for art in articles}
    existing_ids = {art.art_id for art in articles}

    added = 0
    filled = 0
    unchanged = 0
    disk_file_set = set(disk_files)
    new_articles: list[ArticleLang] = []
    for file_name in disk_files:
        default_author = DEFAULT_AUTHOR
        default_lang = get_section(file_name)
        default_title = Path(file_name).stem

        if file_name not in registry_by_file:
            new_id = _allocate_art_id(existing_ids)
            existing_ids.add(new_id)
            new_articles.append(
                ArticleLang(
                    art_id=new_id,
                    file_name=file_name,
                    title=default_title,
                    author=default_author,
                    lang=default_lang,
                )
            )
            added += 1
            continue

        old_art = registry_by_file[file_name]
        new_author = old_art.author
        new_lang = old_art.lang
        new_title = old_art.title
        if not old_art.author.strip():
            new_author = default_author
        if not old_art.lang.strip():
            new_lang = default_lang
        if not old_art.title.strip():
            new_title = default_title
        if (
            new_author != old_art.author
            or new_lang != old_art.lang
            or new_title != old_art.title
        ):
            new_articles.append(
                old_art.model_copy(
                    update={"author": new_author, "lang": new_lang, "title": new_title}
                )
            )
            filled += 1
        else:
            new_articles.append(old_art)
            unchanged += 1

    for art in articles:
        if art.file_name not in disk_file_set:
            new_articles.append(art)

    save_articles(new_articles)

    if added == 0 and filled == 0 and unchanged > 0:
        flash(request, "Все записи уже полные", "info")
    else:
        flash(
            request,
            f"Добавлено: {added}, заполнено: {filled}, без изменений: {unchanged}",
            "success",
        )

    return RedirectResponse("/art_manage", status_code=303)


# ==============================================================================
# ++++++++++++++++++++++++++ art_manage_prune_missing +++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@router_articles.post("/art_manage/prune_missing", name="art_main.art_manage_prune_missing")
async def art_manage_prune_missing(request: Request, _user=Depends(require_login)):
    await validate_csrf(request)

    disk_files = set(scan_content_art())
    articles = list(get_articles())
    kept = [a for a in articles if a.file_name in disk_files]
    removed = len(articles) - len(kept)
    if removed > 0:
        save_articles(kept)
        flash(request, f"Удалено записей: {removed}", "success")
    else:
        flash(request, "Записей без файла нет", "info")
    return RedirectResponse("/art_manage", status_code=303)


# ==============================================================================
# +++++++++++++++++++++++++++++ art_manage_meta ++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@router_articles.post("/art_manage/meta", name="art_main.art_manage_meta")
async def art_manage_meta(
    request: Request,
    _user=Depends(require_login),
    file_name: str = Form(""),
    author: str = Form(""),
    lang: str = Form(""),
    title: str = Form(""),
):
    await validate_csrf(request)

    file_name = file_name.strip()
    author = author.strip()
    lang = lang.strip()
    title = title.strip()

    disk_files = set(scan_content_art())
    articles = list(get_articles())
    registry_by_file = {art.file_name: art for art in articles}

    if file_name not in disk_files and file_name not in registry_by_file:
        flash(request, f"Недопустимое имя файла: {file_name}", "danger")
        return RedirectResponse("/art_manage", status_code=303)

    existing_ids = {art.art_id for art in articles}

    if file_name in registry_by_file:
        old_art = registry_by_file[file_name]
        updated_art = old_art.model_copy(update={"author": author, "lang": lang, "title": title})
        articles = [updated_art if art.file_name == file_name else art for art in articles]
        action_word = "Обновлена"
    else:
        new_id = _allocate_art_id(existing_ids)
        if not title:
            title = Path(file_name).stem
        articles.append(
            ArticleLang(
                art_id=new_id,
                file_name=file_name,
                title=title,
                author=author,
                lang=lang,
            )
        )
        action_word = "Добавлена"

    save_articles(articles)
    flash(request, f"{action_word} запись для {file_name}", "success")
    return RedirectResponse("/art_manage", status_code=303)


# ==============================================================================
# +++++++++++++++++++++++++++++++ helpers ++++++++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
def _is_complete(art: ArticleLang) -> bool:
    return bool(art.author.strip() and art.lang.strip() and art.title.strip())


def _allocate_art_id(existing_ids: set[int]) -> int:
    new_id = int(time.time())
    while new_id in existing_ids:
        new_id += 1
    return new_id
