# app/domains/inference/utils.py

import os
import uuid
from PIL import Image


ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png"}


def is_image_filename(filename: str) -> bool:
    """
    확장자로 1차 검증 (jpg/png만 허용)
    """
    ext = os.path.splitext(filename.lower())[1]
    return ext in ALLOWED_IMAGE_EXT


def load_image_pil(file_path: str) -> Image.Image:
    """
    저장된 파일을 PIL 이미지로 로드
    """
    img = Image.open(file_path)
    return img.convert("RGB")


def make_uuid_filename(original_filename: str) -> str:
    """
    원본 확장자는 유지하고, 파일명만 UUID로 바꾼다.
    """
    ext = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4().hex}{ext}"
