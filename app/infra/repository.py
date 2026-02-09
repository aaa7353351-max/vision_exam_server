# app/infra/repository.py

from datetime import datetime
from typing import Optional, List, Dict, Any

from bson import ObjectId
from pymongo.collection import Collection

from app.infra.db import db
from app.core.config import COLLECTION_NAME


def get_collection() -> Collection:
    return db[COLLECTION_NAME]


def insert_inference_result(
    original_filename: str,
    saved_path: str,
    model_name: str,
    topk: List[Dict[str, Any]],
) -> str:
    """
    결과를 MongoDB에 저장하고, 생성된 _id(ObjectId)를 문자열로 반환
    """
    col = get_collection()

    doc = {
        "original_filename": original_filename,
        "saved_path": saved_path,
        "model_name": model_name,
        "topk": topk,
        "created_at": datetime.utcnow(),  # datetime으로 저장 (요구사항 OK)
    }

    result = col.insert_one(doc)
    return str(result.inserted_id)


def find_inference_by_id(id_str: str) -> Optional[Dict[str, Any]]:
    """
    ObjectId 문자열로 단건 조회. 없으면 None 반환
    """
    if not ObjectId.is_valid(id_str):
        return None

    col = get_collection()
    doc = col.find_one({"_id": ObjectId(id_str)})

    if not doc:
        return None

    # ObjectId는 JSON으로 바로 못 나가니까 문자열로 변환
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc


def list_inference_results(
    skip: int = 0,
    limit: int = 10,
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    목록 조회(페이징 + 선택 필터)
    반환: items, skip, limit, count
    """
    col = get_collection()

    query = {}
    if model_name:
        query["model_name"] = model_name

    count = col.count_documents(query)

    cursor = (
        col.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    items = []
    for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        items.append(doc)

    return {
        "items": items,
        "skip": skip,
        "limit": limit,
        "count": count,
    }
