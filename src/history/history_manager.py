import json;
from datetime import datetime;
from pathlib import Path;
from ..utils.constants import HISTORY_MAX;
from ..utils.async_io import writer;


class HistoryManager:
    def __init__(self, base_dir: Path):
        self._file = base_dir / "history.json";
        base_dir.mkdir(parents=True, exist_ok=True);
        self._entries: list[dict] = self._load();

    def _load(self) -> list[dict]:
        if self._file.exists():
            try:
                return json.loads(self._file.read_text());
            except Exception:
                return [];
        return [];

    def _save(self):
        writer().write(self._file, self._entries);

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

    def remove(self, visited_at: str):
        for i, entry in enumerate(self._entries):
            if entry.get("visited_at") == visited_at:
                self._entries.pop(i);
                self._save();
                return;

    def clear(self):
        self._entries = [];
        self._save();
