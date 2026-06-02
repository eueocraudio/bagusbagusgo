import json;
from pathlib import Path;
from ..utils.async_io import writer;


class BookmarkManager:
    def __init__(self, base_dir: Path):
        self._file = base_dir / "bookmarks.json";
        base_dir.mkdir(parents=True, exist_ok=True);
        self._bookmarks: list[dict] = self._load();

    def _load(self) -> list[dict]:
        if self._file.exists():
            try:
                return json.loads(self._file.read_text());
            except Exception:
                return [];
        return [];

    def _save(self):
        writer().write(self._file, self._bookmarks);

    def all(self) -> list[dict]:
        return list(self._bookmarks);

    def contains(self, url: str) -> bool:
        return any(b["url"] == url for b in self._bookmarks);

    def add(self, title: str, url: str):
        if not self.contains(url):
            self._bookmarks.append({"title": title, "url": url});
            self._save();

    def remove(self, url: str):
        self._bookmarks = [b for b in self._bookmarks if b["url"] != url];
        self._save();

    def rename(self, url: str, new_title: str):
        for b in self._bookmarks:
            if b["url"] == url:
                b["title"] = new_title;
                break;
        self._save();
