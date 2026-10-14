# 📚 Book Concierge (나만의 맞춤형 AI 도서 컨시어지)

![Book Concierge Demo](./demo.gif)

사용자의 독서 취향과 독서 이력을 장기 기억(Memory Bank)하고, Firestore 기반 내 서재(독서 목록)를 관리하며, 생성형 AI를 통해 맞춤 도서 추천과 가상 북커버 표지 일러스트를 생성해 주는 **ADK / Agent Platform 기반 대화형 북 큐레이터 에이전트**입니다.

---

## ✨ 실제로 구현된 기능 (Implemented Features)

### 1. 🧠 Vertex AI Memory Bank (장기 기억 관리)
- **`PreloadMemoryTool` & `generate_memories_callback`**: 대화 시작 시 과거 사용자 선호 장르(SF, 과학 등), 좋아하는 작가, 완독한 책 목록 및 평점을 불러옵니다.
- **자동 메모리 축적**: 대화 종료 콜백(`after_agent_callback`)을 통해 사용자가 언급한 새로운 취향과 완독 이력을 자동으로 장기 메모리에 기록·동기화합니다.

### 2. 🗄️ Google Cloud Firestore (내 서재 데이터베이스)
- **도서 목록 및 상태 조회 (`list_bookshelf`)**: 읽는 중(`reading`), 완독(`completed`), 위시리스트(`wishlist`) 등 상태별 필터링 조회.
- **서재 등록 및 업데이트 (`add_or_update_book`)**: 신규 도서 등록, 읽은 페이지 수 및 전체 페이지 진행도 갱신, 평점 및 독서 메모 저장.
- **큐레이션 도서 풀 (`get_curated_books`)**: 장르별 추천 도서 목록 및 줄거리 메타데이터 조회.

### 3. 🌐 외부 공개 도서 데이터베이스 연동 (Open Library API)
- **공개 도서 검색 (`search_public_books`)**: Open Library Search API를 연동하여 실제 도서의 저자, 출판 연도, 초판 연도 등을 실시간 검색.

### 4. 🎨 Gemini 이미지 생성 및 Google Cloud Storage (AI 북커버 일러스트)
- **이미지 생성 (`generate_book_cover`)**: `gemini-3.1-flash-lite-image` 모델을 활용하여 도서 컨셉에 맞는 고품질 북커버 일러스트 생성.
- **세션 아티팩트 저장**: `tool_context.save_artifact`를 통해 ADK Dev UI(Playground) Artifacts 탭에 표시.
- **GCS 퍼블릭 업로드**: 생성된 이미지 바이트를 공개 Cloud Storage 버킷에 직접 업로드하여 영구적인 HTTPS URL(`https://storage.googleapis.com/...`) 반환.

### 5. 💻 Agent Engine Sandbox Python 코드 실행 (`code_executor`)
- **격리된 샌드박스 실행 (`AgentEngineSandboxCodeExecutor`)**: Agent Platform의 관리형 격리 환경에서 Python 코드를 안전하게 실행하여 수치 계산 및 데이터 처리 수행.

### 6. 🃏 A2UI v0.8 리치 카드 UI (Agent-to-User Interface)
- **A2UI Schema Manager (v0.8 Basic Catalog)**: `Card`, `Column`, `Row`, `Text`, `Image`, `Divider` 등을 사용하여 일반 텍스트가 아닌 구조화된 시각 카드로 응답 렌더링.
- **후처리 콜백 (`a2ui_callback`)**: 모델의 A2UI JSON 출력을 캡처하여 클라이언트 렌더러가 처리 가능한 표준 이벤트 블록으로 변환.

### 7. 🚀 FastAPI A2A 프록시 & 맞춤 웹 채팅 UI (`frontend/`)
- **A2A 프로토콜 통신**: 에이전트 런타임과 표준 A2A(Agent-to-Agent) 통신 수행.
- **반응형 웹 UI**:
  - 도서 컨시어지 브랜드 컬러(바이올렛/인디고) 및 아바타 프로필 기반 대화 말풍선 레이아웃.
  - 자주 묻는 질문 원클릭 칩 버튼 3개 배치 (`서재 현황 확인`, `맞춤 도서 추천`, `북커버 표지 생성`).
  - 내장 A2UI 미니 렌더러 탑재.

---

## 📌 계획됨 (미구현 항목)

`project_brief.md`에 계획되었으나 현재 구현 범위에 포함되지 않은 기능입니다:
- ⏳ **완독 예상 일수 및 연간 목표 달성률 자동 계산 전용 도구 [계획됨 (미구현)]**: 현재 Python Code Executor 샌드박스를 통해 임의 계산은 가능하지만, 독서 속도(분당 페이지 수)나 연간 목표치를 체계적으로 추적하는 전용 파라미터화 도구는 아직 구현되지 않았습니다.
- ⏳ **Google Books 공식 API 키 연동 [계획됨 (미구현)]**: 현재는 무료 공개 엔드포인트인 Open Library Search API로 대체 구현되어 있으며, Google Books 전용 API 연동은 미구현 상태입니다.

---

## 🛠️ 로컬 개발 및 실행 안내 (Local Getting Started)

임시 엔드포인트나 외부 접속 주소 없이, 로컬 환경에서 에이전트와 프론트엔드를 설치하고 실행하는 방법입니다.

### 사전 요구 사항
- Python 3.11 이상
- `uv` 패키지 관리자
- Google Cloud SDK (`gcloud` CLI) 로그인 및 프로젝트 설정

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
```

### 1. 에이전트 백엔드 실행 (ADK Web Playground)

프로젝트 루트 폴더(`book-concierge`)에서 의존성을 설치하고 ADK 로컬 웹 서버를 실행합니다:

```bash
cd book-concierge

# 의존성 설치 및 동기화
uv sync

# Memory Bank가 연결된 로컬 ADK Web 실행
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://<YOUR_MEMORY_BANK_ID>
```

### 2. 프론트엔드 웹 서버 실행 (`frontend/`)

별도의 터미널에서 프론트엔드 폴더로 이동한 뒤 전용 가상환경을 구성하고 실행합니다:

```bash
cd book-concierge/frontend

# 가상환경 생성 및 의존성 설치
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 환경 변수 설정 후 서버 실행
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/<LOCATION>/reasoningEngines/<RESOURCE_ID>"
export AGENT_DIRECTORY="app"
export PORT="8080"

python main.py
```

---

## 📂 프로젝트 구조

```
book-concierge/
├── app/
│   ├── agent.py            # Root Agent 정의, 모델 및 콜백, 코드 실행기 연결
│   ├── tools.py            # Firestore 서재, Open Library 검색, AI 이미지 생성 도구
│   ├── a2ui_utils.py       # A2UI 이벤트 변환 콜백
│   ├── a2ui_prompt.txt     # A2UI v0.8 시스템 프롬프트 및 카탈로그 스펙
│   └── fast_api_app.py     # 로컬 FastAPI 서버 래퍼
├── frontend/
│   ├── main.py             # A2A 프로토콜 통신 FastAPI 프록시
│   ├── requirements.txt    # 프론트엔드 의존성
│   └── static/
│       └── index.html      # A2UI 렌더러 및 리브랜딩된 채팅 UI
├── demo.gif                # 실제 동작 시연 녹화 GIF (README 임베드용)
├── agents-cli-manifest.yaml# Agent Engine 배포 매니페스트
└── pyproject.toml          # 에이전트 백엔드 종속성 정의
```
