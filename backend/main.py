from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routers import submissions, topics, problems, chat, chat_sessions
from .config import settings
from .database import create_db_and_tables

app = FastAPI(title="Math Assignment Assistant")

# Initialize database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(chat_sessions.router)
app.include_router(submissions.router)
app.include_router(topics.router)
app.include_router(problems.router)
settings.UPLOADS_DIR.mkdir(exist_ok=True)
app.mount(settings.UPLOAD_URL_PREFIX, StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")


@app.get("/")
def read_root():
    return {"message": "Math Solving Assistant Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)