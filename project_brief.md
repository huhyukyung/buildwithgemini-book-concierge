# My agent: Book Concierge (나만의 맞춤형 AI 도서 컨시어지)
One-liner: 사용자의 취향, 선호 장르 및 독서 이력을 기억하여 맞춤 도서를 추천하고, 독서 목록(서재)을 관리하며, 도서 표지 일러스트를 생성해 주는 대화형 북 큐레이터 에이전트.

Tool coverage:
- Memory: 사용자의 선호 장르(SF, 추리, 인문학 등), 좋아하는 작가, 비선호 주제, 최근 읽은 책 및 평점
- Tools: 내 서재(독서 목록) 조회 및 상태(읽는 중, 완독, 위시리스트) 업데이트 도구, 무료 공개 도서 API(Open Library / Google Books) 검색 도구
- Catalog/UI: 추천 도서 카드 목록, 내 독서 상태 및 진행률 표 (A2UI 연동)
- Image gen: 추천 도서나 가상 도서의 맞춤형 북커버/표지 일러스트 생성
- Sandbox: 완독 예상 일수 계산, 독서 속도 및 연간 목표 달성률 계산

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Open Library / Google Books Public API for real book metadata, Cloud Storage for book cover images
