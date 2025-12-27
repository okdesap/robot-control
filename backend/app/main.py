"""
Main FastAPI App - MINIMAL
"""
from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.v1 import control, stt, tts


# Load backend/.env if present (useful for local dev & WSL)
load_dotenv()


app = FastAPI(title="Robot Control Backend")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
