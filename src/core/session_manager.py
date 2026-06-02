import json;
from pathlib import Path;


class SessionManager:
    def __init__(self, data_dir: Path):
        self._file = data_dir / "session.json";
        data_dir.mkdir(parents=True, exist_ok=True);

    def save(self, urls: list[str]):
        valid = [u for u in urls if u and u != "about:blank"];
        self._file.write_text(json.dumps({"urls": valid}, ensure_ascii=False, indent=2));

    def load(self) -> list[str]:
        if not self._file.exists():
            return [];
        try:
            data = json.loads(self._file.read_text());
            return [u for u in data.get("urls", []) if u];
        except Exception:
            return [];

    def clear(self):
        if self._file.exists():
            self._file.unlink();
