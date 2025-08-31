from fastapi import FastAPI
import uvicorn

from routes import ingest_document, chat

app = FastAPI()
app.include_router(ingest_document.router)
app.include_router(chat.router)


@app.get("/", tags=["health-check"], summary="Health check endpoint")
async def read_root():
    """
    A simple health check endpoint to ensure the API is running.
    Returns a success message.
    """
    return {"message": "API is operational"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )