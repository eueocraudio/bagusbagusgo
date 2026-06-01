import json;
from datetime import datetime;
from .constants import HISTORY_FILE, HISTORY_MAX;


class HistoryManager:
    def __init__(self):
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True);
        self._entries: list[dict] = self._load();

    def _load(self) -> list[dict]:
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text());
            except Exception:
                return [];
        return [];

    def _save(self):
        HISTORY_FILE.write_text(json.dumps(self._entries, ensure_ascii=False, indent=2));

    def record(self, title: str, url: str):
        if not url or url == "about:blank":
            return;
        self._entries.append({
            "title": title or url,
            "url": url,
            "visited_at": datetime.now().isoformat(timespec="seconds"),
        });
        if len(self._entries) > HISTORY_MAX:
            self._entries = self._entries[-HISTORY_MAX:];
        self._save();

    def all(self) -> list[dict]:
        return list(reversed(self._entries));

    def search(self, query: str) -> list[dict]:
        q = query.lower();
        return [e for e in self.all() if q in e["title"].lower() or q in e["url"].lower()];

    def remove(self, index_in_reversed: int):
        real = len(self._entries) - 1 - index_in_reversed;
        if 0 <= real < len(self._entries):
            self._entries.pop(real);
            self._save();

    def clear(self):
        self._entries = [];
        self._save();
