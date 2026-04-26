import socket
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

VERSION = "0.1.0"

THIS_DIR = Path(__file__).parent
STATIC_DIR = THIS_DIR / "static"
TEMPLATES_DIR = THIS_DIR / "templates"

ROUTER = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)


def get_info(request: Request) -> dict[str, str]:
    return {
        "version": VERSION,
        "hostname": socket.gethostname(),
        "clientIP": request.client.host,
    }


# this function guesses if the client that sent the request is a full-fledged
# graphical web browser and not a text-based tool such as curl
# graphical browsers typically send accept: text/html,application/xhtml+xml,...
# curl sends accept: */*
@ROUTER.get("/")
def root(request: Request):
    """
    Root path dynamically redirects the request to /html or /text
    based on if the request is coming from browser or curl.

    If the accept header is "application/json", it serves the information in JSON format.
    """
    # get the accept header
    accept_header = request.headers.get("accept", "")
    print(f"Accept header: {accept_header}")

    # if the accept header is */*, redirect to the text version
    if accept_header.startswith("*/*"):
        print("Redirecting to the text version...")
        return RedirectResponse(url="/text")

    # if the accept header is text/html, redirect to the html version
    if accept_header.startswith("text/html"):
        print("Redirecting to the html version...")
        return templates.TemplateResponse(
            request=request,
            name="redirect.html",
            context={
                "delay": 2,
                "target": "/html",
                "message": "Redirecting to the html version...",
            },
        )

    # if the accept header is "application/json", redirect to the json version
    if accept_header == "application/json":
        print("Serving the json version...")
        return JSONResponse(
            content=get_info(request=request),
            media_type="application/json",
        )

    # if the accept header is not any of the above, redirect to the text version
    print("No matching accept header found, redirecting to the text version...")
    return RedirectResponse(url="/text")


@ROUTER.get("/html", response_class=HTMLResponse)
def serve_html_file(request: Request) -> HTMLResponse:
    """Serve the HTML version of the index page."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=get_info(request=request),
        media_type="text/html",
    )


@ROUTER.get("/text", response_class=PlainTextResponse)
def serve_text_file(request: Request):
    """Serve the text version of the index page."""
    return templates.TemplateResponse(
        request=request,
        name="index.txt",
        context=get_info(request=request),
        media_type="text/plain",
    )


@ROUTER.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(
        path=THIS_DIR / "static/favicon.ico",
    )


async def custom_404_handler(request: Request, exc: Exception) -> PlainTextResponse:
    """Handle 404 errors."""
    return PlainTextResponse(
        content=f"'{request.url}' Not Found",
        status_code=status.HTTP_404_NOT_FOUND,
    )


exception_handlers: dict[int, Any] = {
    status.HTTP_404_NOT_FOUND: custom_404_handler,
}

app = FastAPI(
    title="Kiada",
    description="Kiada is a simple web application that shows quotes from the Kubernetes in Action book.",
    version=VERSION,
    exception_handlers=exception_handlers,
)

app.mount(path="/static", app=StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router=ROUTER)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=8080)
