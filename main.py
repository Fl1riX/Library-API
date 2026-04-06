import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.presentation.api.v1.endpoints import router as api_router

app = FastAPI(
    title="Library api", 
    version="0.0.1",
    description="Библиотечная система"
)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_credentials=True
)

@app.get("/")
async def wellcome():
    return {
        "text": "Wellcome to liibrary api!",
        "docs": "http://localhost:8000/docs"
    }

if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=True)