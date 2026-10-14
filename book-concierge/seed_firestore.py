"""Seed script for plant-care-agent Firestore database."""
from google.cloud import firestore

# Hardcoded Project ID per instructions
PROJECT_ID = "qwiklabs-gcp-04-1201f634bbf1"

def seed_database():
    print(f"Connecting to Firestore with project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)

    # 1. Plants Collection
    plants = [
        {
            "id": "monstera-deliciosa",
            "name": "몬스테라 델리시오사 (Monstera Deliciosa)",
            "category": "관엽식물",
            "price": 28000,
            "light_level": "반음지 ~ 밝은 간접광",
            "water_frequency_days": 7,
            "difficulty": "초급",
            "description": "시원하게 갈라진 잎이 매력적인 플랜테리어의 대표 식물입니다.",
            "stock": 15
        },
        {
            "id": "snake-plant",
            "name": "산세베리아 (Sansevieria / Snake Plant)",
            "category": "다육/공기정화",
            "price": 18000,
            "light_level": "음지 ~ 직사광선 모두 가능",
            "water_frequency_days": 21,
            "difficulty": "입문자용 (매우 쉬움)",
            "description": "밤에 산소를 배출하는 뛰어난 공기정화 식물로 건조에 매우 강합니다.",
            "stock": 25
        },
        {
            "id": "fiddle-leaf-fig",
            "name": "떡갈잎고무나무 (Fiddle Leaf Fig)",
            "category": "관엽식물",
            "price": 35000,
            "light_level": "밝은 간접광 필수",
            "water_frequency_days": 10,
            "difficulty": "중급",
            "description": "바이올린을 닮은 넓고 윤기나는 잎을 가진 인기 인테리어 식물입니다.",
            "stock": 8
        },
        {
            "id": "peace-lily",
            "name": "스파티필름 (Peace Lily)",
            "category": "꽃/공기정화",
            "price": 15000,
            "light_level": "반음지",
            "water_frequency_days": 5,
            "difficulty": "초급",
            "description": "우아한 흰 꽃과 싱그러운 잎이 조화를 이루며 물 부족 시 잎이 처져 물주기 타이밍을 알기 쉽습니다.",
            "stock": 20
        }
    ]

    for plant in plants:
        doc_id = plant.pop("id")
        db.collection("plants").document(doc_id).set(plant)
        print(f"  ✓ Plant seeded: {doc_id} ({plant['name']})")

    # 2. Care Logs Collection (초기 기록 샘플)
    care_logs = [
        {
            "user_id": "user_default",
            "plant_id": "monstera-deliciosa",
            "action": "물주기 (Watering)",
            "date": "2026-10-10",
            "notes": "겉흙이 마른 것을 확인하고 화분 밑으로 흘러나올 때까지 흠뻑 줌"
        }
    ]

    for log in care_logs:
        db.collection("care_logs").add(log)
        print(f"  ✓ Care log seeded for: {log['plant_id']}")

    print("Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
