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

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-1201f634bbf1"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client configured with the explicit hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_bookshelf(status: Optional[str] = None) -> str:
    """사용자의 내 서재(bookshelf)에 등록된 도서 목록과 독서 상태(reading, completed, wishlist),
    진행 페이지 수, 평점 및 메모를 조회합니다.

    Args:
        status: 필터링할 독서 상태 ('reading', 'completed', 'wishlist' 중 하나, 생략 시 전체 조회).

    Returns:
        JSON 형식의 서재 도서 목록 문자열.
    """
    db = get_firestore_client()
    docs = db.collection("bookshelf").stream()
    books = []
    for doc in docs:
        data = doc.to_dict()
        if status:
            if data.get("status") == status:
                books.append(data)
        else:
            books.append(data)
    return json.dumps(books, ensure_ascii=False)


def add_or_update_book(
    book_id: str,
    title: str,
    author: str,
    genre: str,
    status: str,
    current_page: int = 0,
    total_pages: int = 300,
    rating: float = 0.0,
    notes: str = "",
) -> str:
    """내 서재에 도서를 새로 등록하거나 독서 상태/진행도/평점을 업데이트합니다.

    Args:
        book_id: 도서 고유 ID (예: 'project_hail_mary', 'dune').
        title: 도서 제목.
        author: 저자명.
        genre: 도서 장르 (예: 'SF', '소설', '인문학').
        status: 독서 상태 ('reading': 읽는 중, 'completed': 완독, 'wishlist': 읽고 싶은 책).
        current_page: 현재까지 읽은 페이지 수.
        total_pages: 전체 페이지 수.
        rating: 별점/평점 (0.0 ~ 5.0).
        notes: 독서 메모 또는 한줄평.

    Returns:
        처리 결과 메시지.
    """
    db = get_firestore_client()
    book_data = {
        "id": book_id,
        "title": title,
        "author": author,
        "genre": genre,
        "status": status,
        "current_page": current_page,
        "total_pages": total_pages,
        "rating": rating,
        "notes": notes,
    }
    db.collection("bookshelf").document(book_id).set(book_data)
    return f"도서 '{title}'이(가) 내 서재에 [{status}] 상태로 등록/업데이트되었습니다."


def get_curated_books(genre: Optional[str] = None) -> str:
    """큐레이션된 추천 도서 풀(curated_books)에서 도서 목록과 줄거리 요약을 조회합니다.

    Args:
        genre: 특정 장르 필터링 (선택 사항, 예: 'SF', '과학').

    Returns:
        JSON 형식의 추천 도서 목록 문자열.
    """
    db = get_firestore_client()
    docs = db.collection("curated_books").stream()
    books = []
    for doc in docs:
        b = doc.to_dict()
        if genre:
            if genre.lower() in b.get("genre", "").lower() or any(genre.lower() in t.lower() for t in b.get("tags", [])):
                books.append(b)
        else:
            books.append(b)
    return json.dumps(books, ensure_ascii=False)


def search_public_books(query: str) -> str:
    """Open Library 무료 공개 API를 사용하여 실제 전 세계 도서 데이터베이스를 검색합니다.
    도서 제목이나 저자명으로 검색하여 제목, 저자, 출판 연도, 초판 연도 등을 실시간으로 반환합니다.

    Args:
        query: 검색할 도서 제목 또는 저자명 (예: 'Dune', 'Isaac Asimov', 'Demian').

    Returns:
        JSON 형식의 도서 검색 결과 문자열.
    """
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://openlibrary.org/search.json?q={encoded_query}&limit=3"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Book-Concierge-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode())
            docs = data.get("docs", [])
            results = []
            for doc in docs[:3]:
                results.append({
                    "title": doc.get("title"),
                    "author_name": doc.get("author_name", ["미상"]),
                    "first_publish_year": doc.get("first_publish_year"),
                    "edition_count": doc.get("edition_count"),
                    "key": doc.get("key"),
                })
            return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Open Library 검색 중 오류 발생: {str(e)}"}, ensure_ascii=False)


async def generate_book_cover(
    title: str,
    prompt_description: str,
    tool_context: Any = None,
) -> str:
    """사용자가 요청한 도서의 가상 북커버 또는 표지 일러스트를 생성합니다.
    생성된 이미지는 세션 아티팩트로 저장되어 Playground의 Artifacts 탭에 표시되며,
    공개 Cloud Storage 버킷에 업로드되어 퍼블릭 웹 URL을 반환합니다.

    Args:
        title: 도서 제목 (예: '프로젝트 헤일메리', '시간의 경계').
        prompt_description: 표지에 들어갈 시각적 장면 묘사 (예: '광활한 우주를 배경으로 빛나는 별들과 작은 우주선').
        tool_context: ADK 도구 컨텍스트 (아티팩트 저장용, 프레임워크가 자동 주입).

    Returns:
        JSON 형식의 생성 결과 및 퍼블릭 이미지 URL 문자열.
    """
    import uuid
    from google import genai
    from google.cloud import storage
    from google.genai import types

    bucket_name = "chef-gemini-images-qwiklabs-gcp-04-1201f634bbf1"
    image_prompt = (
        f"A beautiful, artistic book cover illustration for a book titled '{title}'. "
        f"Visual details: {prompt_description}. Highly detailed, masterpiece quality book cover art, no garbled text."
    )

    try:
        # 1. Generate image using gemini-3.1-flash-lite-image in global location
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=image_prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return json.dumps({"error": "이미지 생성 모델에서 이미지 데이터를 반환받지 못했습니다."}, ensure_ascii=False)

        # 2. Save artifact to Playground if tool_context is provided
        ext = "png" if "png" in mime_type else "jpg"
        filename = f"cover_{uuid.uuid4().hex[:8]}.{ext}"

        if tool_context and hasattr(tool_context, "save_artifact"):
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            await tool_context.save_artifact(
                filename=filename,
                artifact=artifact_part,
                custom_metadata={"title": title, "type": "book_cover"},
            )

        # 3. Upload to Google Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{bucket_name}/{filename}"

        return json.dumps({
            "success": True,
            "title": title,
            "public_url": public_url,
            "filename": filename,
            "message": f"도서 '{title}'의 표지 일러스트가 성공적으로 생성되었습니다.",
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"도서 표지 생성 중 오류 발생: {str(e)}"}, ensure_ascii=False)

