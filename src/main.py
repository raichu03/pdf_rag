from typing import Dict, Any

from fastapi import FastAPI
import uvicorn

from routes import ingest_document, chat

app: FastAPI = FastAPI()
app.include_router(ingest_document.router)
app.include_router(chat.router)


@app.get("/", tags=["health-check"], summary="Health check endpoint")
async def read_root() -> Dict[str, str]:
    """Health check endpoint to ensure the API is running."""
    return {"message": "API is operational"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )