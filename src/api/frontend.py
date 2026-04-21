from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST_DIR = ROOT_DIR / "frontend" / "dist"
FRONTEND_INDEX_PATH = FRONTEND_DIST_DIR / "index.html"


def mount_frontend_assets(app) -> None:
    assets_dir = FRONTEND_DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")


def serve_frontend_app() -> FileResponse:
    if not FRONTEND_INDEX_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail={
                "error_code": "FRONTEND_BUILD_MISSING",
                "message": "frontend build output was not found; run npm run build in frontend/",
            },
        )
    return FileResponse(FRONTEND_INDEX_PATH)
