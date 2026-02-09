# app/domains/inference/vision.py

from typing import List, Dict

import torch
from torchvision import models, transforms
from torchvision.models import (
    ResNet18_Weights,
    MobileNet_V3_Large_Weights,
    EfficientNet_B0_Weights,
)

# ✅ 지원 모델 목록 (시험 요구사항)
SUPPORTED_MODELS = {"resnet18", "mobilenet_v3", "efficientnet_b0"}


def _get_model_and_weights(model_name: str):
    """
    model_name에 따라 pretrained weights와 모델을 준비한다.
    """
    if model_name == "resnet18":
        weights = ResNet18_Weights.DEFAULT
        model = models.resnet18(weights=weights)
        return model, weights

    if model_name == "mobilenet_v3":
        weights = MobileNet_V3_Large_Weights.DEFAULT
        model = models.mobilenet_v3_large(weights=weights)
        return model, weights

    if model_name == "efficientnet_b0":
        weights = EfficientNet_B0_Weights.DEFAULT
        model = models.efficientnet_b0(weights=weights)
        return model, weights

    return None, None


def predict_topk(image_pil, model_name: str, top_k: int = 3) -> List[Dict]:
    """
    PIL 이미지를 받아서 Top-K 분류 결과를 반환한다.
    반환 형태:
    [{"label": "...", "score": 0.87}, ...]
    """
    if model_name not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported model_name: {model_name}")

    if top_k <= 0 or top_k > 10:
        raise ValueError("top_k must be between 1 and 10")

    model, weights = _get_model_and_weights(model_name)

    # 모델 준비
    model.eval()

    # weights에 맞는 전처리
    preprocess = weights.transforms()

    # 텐서 변환 (배치 차원 추가)
    x = preprocess(image_pil).unsqueeze(0)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]

    # Top-K
    values, indices = torch.topk(probs, k=top_k)

    # label 매핑 (ImageNet 클래스 이름)
    categories = weights.meta["categories"]

    results = []
    for score, idx in zip(values.tolist(), indices.tolist()):
        results.append(
            {
                "label": categories[idx],
                "score": round(float(score), 6),
            }
        )

    return results
