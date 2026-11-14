import json
import os
import time

DETAIL_LEVELS = ["brief", "normal", "detailed"]
RATINGS = ["too_short", "good", "too_long"]


class StudentMemory:
    """Persistent memory: the student's preferences plus their feedback history."""

    def __init__(self, path="data/student_memory.json"):
        self.path = path
        self.profile = {"detail": "normal"}
        self.history = []
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            self.profile.update(data.get("profile", {}))
            self.history = data.get("history", [])
        except (json.JSONDecodeError, OSError):
            pass  # unreadable file: start fresh instead of crashing

    def save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"profile": self.profile, "history": self.history}, f, indent=2)

    def record_feedback(self, rating, comment=""):
        """Log feedback and adapt: too_short raises the detail level, too_long lowers it."""
        if rating not in RATINGS:
            raise ValueError(f"rating must be one of {RATINGS}")

        level = DETAIL_LEVELS.index(self.profile["detail"])
        if rating == "too_short":
            level = min(level + 1, len(DETAIL_LEVELS) - 1)
        elif rating == "too_long":
            level = max(level - 1, 0)
        self.profile["detail"] = DETAIL_LEVELS[level]

        self.history.append(
            {
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "rating": rating,
                "comment": comment,
                "detail_after": self.profile["detail"],
            }
        )
        self.save()


if __name__ == "__main__":
    test_path = "data/_test_memory.json"
    if os.path.exists(test_path):
        os.remove(test_path)

    memory = StudentMemory(test_path)
    print("Start:", memory.profile)

    memory.record_feedback("too_short", "I want more detail")
    print("After 'too_short':", memory.profile)

    memory.record_feedback("too_long")
    memory.record_feedback("too_long")
    print("After two 'too_long':", memory.profile)

    reloaded = StudentMemory(test_path)
    print("Reloaded from file:", reloaded.profile, f"({len(reloaded.history)} feedback events)")

    os.remove(test_path)