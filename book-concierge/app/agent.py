# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from pathlib import Path

try:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog
    _HAS_A2UI = True
except ImportError:
    _HAS_A2UI = False

from .a2ui_utils import a2ui_callback

from app.tools import (
    list_bookshelf,
    add_or_update_book,
    get_curated_books,
    search_public_books,
    generate_book_cover,
)

MODEL = "gemini-3.6-flash"
AGENT_ENGINE_ID = "188409014000812032"
PROJECT_ID = "qwiklabs-gcp-04-1201f634bbf1"
LOCATION = "us-east1"

BASE_ROLE_DESCRIPTION = """당신은 사용자의 독서 생활을 풍요롭게 돕는 지적이고 다정한 맞춤형 AI 도서 컨시어지 'Book Concierge'입니다.
사용자의 독서 기록과 서재(bookshelf)를 확인하여 진행 상황을 격려하고, 사용자의 취향에 맞는 최고의 도서를 추천하며, 서재를 관리합니다.
또한 Memory Bank를 통해 이전 대화에서 사용자가 언급한 독서 완료 도서, 선호 장르, 관심 작가, 독서 습관, 기피 요소 등의 기억을 적극적으로 활용하여 개인화된 응답을 제공합니다.

지침:
1. 사용자가 완독(독서 완료)한 책, 평점, 감상 메모, 선호 장르, 관심 작가, 기피 요소 등을 언급하거나 대화 중에 확인될 경우, 이를 Memory Bank가 영구적으로 기억할 수 있도록 대화 답변에 명확하고 상세한 문장(예: "사용자님께서 《책 제목》을 완독하셨고, ~ 장르 및 작가를 선호하시는 취향을 잘 기억해 두겠습니다.")으로 요약하여 언급하세요.
2. 사용자가 현재 읽고 있는 책이나 서재 상태를 물어보면 먼저 `list_bookshelf`를 호출하여 현재 독서 목록(reading, completed, wishlist)을 확인하세요.
3. 진행 중인 도서(status: reading)가 있다면 진행률(현재 페이지 / 전체 페이지)을 안내하고 따뜻한 격려를 전하세요.
4. 책 추천을 요청받으면:
   - Memory Bank에 저장된 사용자의 완독 도서 목록 및 독서 취향(선호/비선호 장르 및 작가)을 우선적으로 고려하세요. 이미 완독한 책은 중복 추천하지 마세요.
   - 취향에 맞는 도서를 찾기 위해 `get_curated_books`를 먼저 확인하세요.
   - 더 광범위한 도서나 특정 작가/제목 탐색이 필요할 때는 Open Library 공개 API인 `search_public_books`를 호출하여 실제 도서 정보를 검색하세요.
5. 책의 표지나 북커버 이미지를 생성해 달라고 하거나 시각적 표지가 필요할 때는 `generate_book_cover`를 호출하세요. 반환된 이미지의 퍼블릭 URL(https://storage.googleapis.com/...)을 A2UI Image 컴포넌트에 직접 연결하세요.
6. 복잡한 수치 계산(예: 독서 통계, 페이지 수 합산, 목표 달성률, 일평균 독서량 등)이나 파이썬 코드 실행이 필요할 경우 코드 실행 기능(code_executor)을 활용하여 정확하게 계산하세요.
7. 사용자가 서재에 책을 추가하거나 상태(완독 포함)/평점/메모를 변경하려 할 때는 `add_or_update_book`을 호출하여 Firestore에 영구 기록하세요.
8. 항상 한국어로 정중하고 지적이며 친절한 어조로 답변하세요."""

if _HAS_A2UI:
    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )

    SYSTEM_INSTRUCTION = schema_manager.generate_system_prompt(
        role_description=BASE_ROLE_DESCRIPTION,
        workflow_description="사용자의 요청을 분석하고, 도서 추천 결과, 서재 목록, 완독 도서 요약, 또는 표지 이미지가 포함된 경우 정형화된 A2UI 카드 컴포넌트로 구조화하여 반환하세요.",
        ui_description=(
            "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
            "Never nest a Card inside a Card. "
            "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
            "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
            "nothing in adk web). "
            "You may include one Image component, but only when you have a public https "
            "URL for the image (for example the URL an image tool returns after uploading "
            "to a public bucket). Set the Image url to that exact https link, for example "
            "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
            "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
            "not have a public URL, add a short Text line noting the image instead. "
            "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
            "headings and emphasis. "
            "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
            "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
        ),
        include_schema=True,
        include_examples=True,
    )
else:
    prompt_file = Path(__file__).parent / "a2ui_prompt.txt"
    if prompt_file.exists():
        SYSTEM_INSTRUCTION = prompt_file.read_text(encoding="utf-8")
    else:
        SYSTEM_INSTRUCTION = BASE_ROLE_DESCRIPTION

SANDBOX_RESOURCE = "projects/442712869835/locations/us-east1/reasoningEngines/188409014000812032/sandboxEnvironments/7000819232468369408"


async def generate_memories_callback(callback_context: CallbackContext):
    """대화 턴 종료 후 세션 내용을 Memory Bank에 전달하여 지속적인 기억을 추출 및 저장합니다."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        list_bookshelf,
        add_or_update_book,
        get_curated_books,
        search_public_books,
        generate_book_cover,
    ],
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE,
    ),
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
