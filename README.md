# VisionCloud - CV Inference Server (FastAPI + MongoDB)

이미지 업로드 → 사전학습(pretrained) 컴퓨터비전 모델 추론 → 결과 MongoDB 저장/조회까지 한 번에 수행하는 서버입니다.

## 1. 기술 스택

- Python 3.x
- FastAPI
- MongoDB (Community Server)
- PyTorch + torchvision (pretrained)
- PIL(Pillow)

---

## 2. 프로젝트 구조 (DDD 스타일)

app/
├─ main.py # FastAPI 앱 엔트리포인트
│
├─ core/ # 공통 설정 / 에러 정의
│ ├─ config.py # DB 설정, uploads 경로
│ └─ errors.py # 공통 예외 정의 (확장용)
│
├─ infra/ # 외부 시스템 연동 (MongoDB)
│ ├─ db.py # MongoDB 연결
│ └─ repository.py # 추론 결과 저장/조회
│
├─ domains/ # 도메인 단위 기능
│ ├─ health/
│ │ └─ router.py # GET /health
│ │
│ └─ inference/ # 이미지 추론 도메인
│ ├─ router.py # /inference API
│ ├─ schemas.py # 요청/응답 스키마
│ ├─ service.py # 비즈니스 로직 (확장용)
│ ├─ utils.py # 파일/이미지 유틸
│ └─ vision.py # 모델 로딩 + Top-K 추론
│
└─ uploads/ # 업로드 이미지 저장 폴더
└─ .gitkeep

---

## 3. MongoDB 스키마 설명

- DB 이름: `vision_exam`
- Collection 이름: `inference_results`

Document 필드:

- `_id`: ObjectId (MongoDB 자동 생성)
- `original_filename`: str (원본 파일명)
- `saved_path`: str (서버 저장 경로)
- `model_name`: str (사용한 모델명)
- `topk`: list (Top-K 결과)
- `created_at`: datetime (저장 시간)

topk 예시:

```json
[
  { "label": "tabby", "score": 0.87 },
  { "label": "tiger_cat", "score": 0.08 },
  { "label": "Egyptian_cat", "score": 0.03 }
]
```

---

## 4. 실행 방법 (Windows + Git Bash 기준)

### 4-1) 가상환경 생성/활성화

```
python -m venv venv
source venv/Scripts/activate

```

### 4-2) 패키지 설치

```
pip install -r requirements.txt

```

### 4-3) MongoDB 실행

- MongoDB Community Server가 설치되어 있고,

- mongodb://localhost:27017 로 접속 가능해야 합니다.

- (추천) MongoDB Compass에서 mongodb://localhost:27017 Connect 확인

### 4-4) 서버 실행

```
uvicorn app.main:app --reload
```

접속:

- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

---

# 5. API 설명

### 5-1) GET /health

    서버 상태 확인

- Response:

```json
{ "status": "ok" }
```

---

### 5-2) POST /inference

이미지 업로드 → 추론 → MongoDB 저장

- Content-Type: multipart/form-data
- Params:
  - file: jpg/png 이미지
  - model_name: resnet18 | mobilenet_v3 | efficientnet_b0
  - top_k: int (기본 3)

- Response 예시:

```json
{
  "id": "6989566580cb72c33fdd5adf",
  "model_name": "resnet18",
  "topk": [
    { "label": "golden retriever", "score": 0.626616 },
    { "label": "Labrador retriever", "score": 0.341824 },
    { "label": "cocker spaniel", "score": 0.020725 }
  ]
}
```

---

### 5-3) GET /inference/{id}

저장된 결과 단건 조회

- 존재하지 않으면 404

### 5-4 GET /inference

결과 목록 조회(페이징)

- Query:
  - skip (기본 0)
  - limit(기본 10, 최대 50)
  - model_name (선택, 필터)
- Response 예시:

```json
{
  "items": [],
  "skip": 0,
  "limit": 10,
  "count": 0
}
```
