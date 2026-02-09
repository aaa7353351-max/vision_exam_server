# app/domains/inference/router.py

import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query

from app.core.config import UPLOAD_DIR
from app.domains.inference.utils import (
    is_image_filename,
    make_uuid_filename,
    load_image_pil,
)
from app.domains.inference.vision import predict_topk, SUPPORTED_MODELS
from app.infra.repository import (
    insert_inference_result,
    find_inference_by_id,
    list_inference_results,
)

router = APIRouter(prefix="/inference", tags=["Inference"])


@router.post("", response_model=dict)
async def create_inference(
    file: UploadFile = File(...),
    model_name: str = Form(...),
    top_k: int = Form(3),
):
    # 1️⃣ 모델명 검증
    if model_name not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail="Unsupported model_name")

    # 2️⃣ 파일명 검증
    if not is_image_filename(file.filename):
        raise HTTPException(status_code=400, detail="Invalid image file")

    # 3️⃣ uploads 폴더 보장
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 4️⃣ 파일 저장 (UUID)
    saved_filename = make_uuid_filename(file.filename)
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(saved_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 5️⃣ 이미지 로드 + 추론
    image = load_image_pil(saved_path)
    topk = predict_topk(image, model_name, top_k)

    # 6️⃣ MongoDB 저장
    inserted_id = insert_inference_result(
        original_filename=file.filename,
        saved_path=saved_path,
        model_name=model_name,
        topk=topk,
    )

    return {
        "id": inserted_id,
        "model_name": model_name,
        "topk": topk,
    }


@router.get("/{id}")
def get_inference(id: str):
    doc = find_inference_by_id(id)
    if not doc:
        raise HTTPException(status_code=404, detail="Inference result not found")
    return doc


@router.get("")
def list_inferences(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    model_name: str | None = None,
):
    return list_inference_results(skip=skip, limit=limit, model_name=model_name)
