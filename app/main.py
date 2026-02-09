# app/main.py

from fastapi import FastAPI

from app.domains.health.router import router as health_router
from app.domains.inference.router import router as inference_router


app = FastAPI(
    title="VisionCloud Inference API",
    description="Image upload → CV inference → MongoDB storage",
    version="1.0.0",
)

# 라우터 등록
app.include_router(health_router)

app.include_router(inference_router)

@app.get("/")
def root():
    return {"message": "VisionCloud API is running"}

