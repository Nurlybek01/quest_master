import json
from pathlib import Path

LEVELS = {
    "Ученик": 0,
    "Мастер пергаментов": 50,
    "Архимаг документов": 100
}

XP_THRESHOLDS = sorted(LEVELS.items(), key=lambda x: x[1])
SAVE_FILE = Path("gamification_state.json")


class GamificationManager:
    def __init__(self):
        self.xp = 0
        self.achievements = set()
        self._load_state()

    def _load_state(self):
        if SAVE_FILE.exists():
            try:
                data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
                self.xp = data.get("xp", 0)
                self.achievements = set(data.get("achievements", []))
            except Exception:
                pass

    def _save_state(self):
        data = {
            "xp": self.xp,
            "achievements": list(self.achievements)
        }
        SAVE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_xp(self, amount: int, achievement: str = None):
        self.xp += amount
        if achievement:
            self.achievements.add(achievement)
        self._save_state()


    def get_current_level(self) -> str:
        for level, threshold in reversed(XP_THRESHOLDS):
            if self.xp >= threshold:
                return level
        return "Ученик"

    def get_max_xp(self) -> int:
        return XP_THRESHOLDS[-1][1]

    def get_achievements_list(self) -> list:
        return sorted(self.achievements)