"""
Main FastAPI App - MINIMAL
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.v1 import control, stt, tts



# Load backend/.env if present (useful for local dev & WSL)
load_dotenv()


app = FastAPI(title="Robot Control Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], # Allow all origins for now -> Should be changed later on
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(control.router, prefix="/api/v1/control", tags=["control"])
app.include_router(stt.router, prefix="/api/v1/stt", tags=["stt"])
app.include_router(tts.router, prefix="/api/v1/tts", tags=["tts"])


@app.get("/")
def root():
    return {
        "name": "Robot Control Backend",
        "docs": "/docs"
    }

def start_server():
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    start_server()
