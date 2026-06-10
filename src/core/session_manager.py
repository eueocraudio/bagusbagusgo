import json;
from pathlib import Path;
from ..utils.async_io import writer;


class SessionManager:
    def __init__(self, base_dir: Path):
        self._file = base_dir / "session.json";
        base_dir.mkdir(parents=True, exist_ok=True);

    def save(self, urls: list[str]):
        valid = [u for u in urls if u and u != "about:blank"];
        writer().write(self._file, {"urls": valid});

    def load(self) -> list[str]:
        if not self._file.exists():
            return [];
        try:
            data = json.loads(self._file.read_text());
            return [u for u in data.get("urls", []) if u];
        except Exception:
            return [];
