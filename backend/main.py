from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routers import topics, submissions
from .config import settings

app = FastAPI(title="Math Solving Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
settings.UPLOADS_DIR.mkdir(exist_ok=True)
app.mount(settings.UPLOAD_URL_PREFIX, StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")

# Include Routers
app.include_router(topics.router)
app.include_router(submissions.router)

@app.get("/")
def read_root():
    return {"message": "Math Solving Assistant Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)