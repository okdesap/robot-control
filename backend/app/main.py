"""
Application entrypoint
"""
import uvicorn
from app.api.fastAPI import create_api_app


app = create_api_app()


def start_server():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    start_server()
