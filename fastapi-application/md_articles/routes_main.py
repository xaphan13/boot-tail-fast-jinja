# ==============================================================================
# +++++++++++++++++++++++++++++++ routes_main ++++++++++++++++++++++++++++++++++
# --------------------------- /, /home, /about ---------------------------------
# ------------------------------------------------------------------------------
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from config_log import logF
from md_articles.web_utils import flash, get_current_user, render_template


router_main = APIRouter(
    tags=["blog main"],
)


# ==============================================================================
# +++++++++++++++++++++++++++++++ home +++++++++++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@router_main.get("/", name="main.home")
@router_main.get("/home", name="main.home")
async def home():
    return RedirectResponse("/art_home", status_code=303)


# ==============================================================================
# +++++++++++++++++++++++++++++++ about ++++++++++++++++++++++++++++++++++++++++
# ------------------------------------------------------------------------------
@router_main.get("/about", name="main.about")
async def about(
    request: Request,
    _user=Depends(get_current_user),
):
    logF.info("'about'")
    flash(request, "About flash message! - success", "success")
    flash(request, "About flash message! - danger", "danger")
    flash(request, "About flash message! - message", "message")
    flash(request, "About flash message! - info", "info")
    flash(request, "About flash message! - warning", "warning")
    return render_template(
        "about.html",
        {"request": request, "title": "About"},
    )
