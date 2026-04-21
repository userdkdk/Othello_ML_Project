from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.frontend import mount_frontend_assets, serve_frontend_app
from api.game_router import router as game_router
from api.training_router import router as training_router


app = FastAPI(title="Othello Runtime API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mount_frontend_assets(app)
app.include_router(game_router)
app.include_router(training_router)


@app.get("/")
def index() -> FileResponse:
    return serve_frontend_app()


@app.get("/training")
def training_dashboard() -> FileResponse:
    return serve_frontend_app()


@app.get("/{full_path:path}")
def spa_fallback(full_path: str) -> FileResponse:
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    return serve_frontend_app()
