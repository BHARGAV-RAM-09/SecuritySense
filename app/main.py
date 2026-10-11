
"""SecuritySense FastAPI application."""

from pathlib import Path
from app.api.routes import router as api_router

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="SecuritySense",
    description=(
        "Evidence-driven security analysis with controlled reproduction "
        "and traceable verification."
    ),
    version="0.1.0",
)
app.include_router(api_router)
# Serve frontend assets once the CSS and JavaScript files are created.
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=str(static_dir)),
    name="static",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report whether the API process is responding."""
    return {
        "status": "healthy",
        "service": "SecuritySense",
    }


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    """Serve the frontend when its HTML file is available."""
    index_file = BASE_DIR / "templates" / "index.html"

    if not index_file.is_file():
        return HTMLResponse(
            content=(
                "<h1>SecuritySense API</h1>"
                "<p>The API is running. The frontend is not ready yet.</p>"
                '<p><a href="/docs">Explore the API documentation</a></p>'
            ),
            status_code=200,
        )

    return HTMLResponse(
        content=index_file.read_text(encoding="utf-8"),
        status_code=200,
    )
