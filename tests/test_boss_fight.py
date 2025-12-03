import time
import uuid
from core.database import save_quest


def generate_100_quests():
    """Генерирует 100 уникальных квестов напрямую в БД."""
    difficulties = ["Лёгкий", "Средний", "Сложный", "Олимпийский"]
    for i in range(100):
        title = f"Босс-квест #{i+1} ({uuid.uuid4().hex[:6]})"
        difficulty = difficulties[i % 4]
        reward = 100 + i * 10
        description = " ".join(["Автогенерированный квест для босс-файта."] * 15)  # ~50+ слов
        deadline = "2025-12-31 23:59:59"

        save_quest(title, difficulty, reward, description, deadline)


def test_100_quests_in_5_seconds():
    """Тест: 100 квестов должны создаться за <5 секунд."""
    start = time.time()
    generate_100_quests()
    elapsed = time.time() - start

    assert elapsed < 5, f"Слишком медленно: {elapsed:.2f} сек"
    print(f"\n✅ Босс повержен за {elapsed:.2f} секунд! +20 XP")