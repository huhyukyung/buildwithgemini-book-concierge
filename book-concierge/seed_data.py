# Copyright 2026 Google LLC
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-1201f634bbf1"

def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    
    # 1. Seed Bookshelf (사용자의 내 서재 / 독서 기록)
    bookshelf_items = [
        {
            "id": "project_hail_mary",
            "title": "프로젝트 헤일메리 (Project Hail Mary)",
            "author": "앤디 위어 (Andy Weir)",
            "genre": "SF / 우주 과학",
            "status": "reading",  # reading, completed, wishlist
            "current_page": 240,
            "total_pages": 690,
            "rating": 5.0,
            "notes": "우주에서 만난 외계인 친구 로키와의 협력 과정이 흥미진진함."
        },
        {
            "id": "dune",
            "title": "듄 1 (Dune)",
            "author": "프랭크 허버트 (Frank Herbert)",
            "genre": "SF / 스페이스 오페라",
            "status": "completed",
            "current_page": 900,
            "total_pages": 900,
            "rating": 4.5,
            "notes": "압도적인 세계관과 생태학적 통찰이 돋보이는 명작."
        },
        {
            "id": "three_body_problem",
            "title": "삼체 1 (The Three-Body Problem)",
            "author": "류츠신 (Cixin Liu)",
            "genre": "하드 SF",
            "status": "wishlist",
            "current_page": 0,
            "total_pages": 440,
            "rating": 0.0,
            "notes": "넷플릭스 시리즈 보기 전 원작 소설로 읽어볼 예정."
        },
        {
            "id": "atomic_habits",
            "title": "아주 작은 습관의 힘 (Atomic Habits)",
            "author": "제임스 클리어 (James Clear)",
            "genre": "자기계발 / 심리",
            "status": "completed",
            "current_page": 340,
            "total_pages": 340,
            "rating": 4.8,
            "notes": "작은 1%의 변화가 만드는 복리 효과. 실생활 적용 중."
        }
    ]

    print("Seeding bookshelf collection...")
    for item in bookshelf_items:
        doc_ref = db.collection("bookshelf").document(item["id"])
        doc_ref.set(item)
        print(f"  + Added to bookshelf: {item['title']} [{item['status']}]")

    # 2. Seed Books Catalog (추천 도서 큐레이션 풀)
    curated_books = [
        {
            "id": "klara_and_the_sun",
            "title": "클라라와 태양 (Klara and the Sun)",
            "author": "가즈오 이시구로",
            "genre": "SF / 문학",
            "description": "인공지능 로봇 클라라의 시선으로 바라본 인간의 사랑과 고독에 관한 깊은 성찰.",
            "total_pages": 376,
            "tags": ["AI", "휴머니즘", "노벨문학상"]
        },
        {
            "id": "ted_chiang_exhalation",
            "title": "숨 (Exhalation)",
            "author": "테드 창",
            "genre": "SF 단편선",
            "description": "시간 여행, 자유의지, 기억의 본질을 철학적으로 탐구한 SF 단편 걸작선.",
            "total_pages": 448,
            "tags": ["철학", "단편", "시간여행"]
        },
        {
            "id": "cosmic_connection",
            "title": "코스모스 (Cosmos)",
            "author": "칼 세이건",
            "genre": "교양 과학 / 천문학",
            "description": "광대한 우주와 생명의 기원에 대한 인류의 탐구 여정을 그린 불멸의 고전.",
            "total_pages": 700,
            "tags": ["우주", "과학", "인문학"]
        }
    ]

    print("Seeding curated_books collection...")
    for book in curated_books:
        doc_ref = db.collection("curated_books").document(book["id"])
        doc_ref.set(book)
        print(f"  + Added curated book: {book['title']}")

    print("✅ Firestore book-concierge seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
