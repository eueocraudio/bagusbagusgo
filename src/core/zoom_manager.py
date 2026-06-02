import json;
from pathlib import Path;
from urllib.parse import urlparse;

DEFAULT_ZOOM = 1.0;
MIN_ZOOM     = 0.25;
MAX_ZOOM     = 5.0;
ZOOM_STEP    = 0.1;


def _clamp(factor: float) -> float:
    return max(MIN_ZOOM, min(MAX_ZOOM, round(factor, 2)));


class ZoomManager:
    def __init__(self, base_dir: Path):
        self._file = base_dir / "zoom.json";
        base_dir.mkdir(parents=True, exist_ok=True);
        self._zooms: dict[str, float] = self._load();

    def _load(self) -> dict[str, float]:
        if self._file.exists():
            try:
                data = json.loads(self._file.read_text());
                return {k: float(v) for k, v in data.items()};
            except Exception:
                return {};
        return {};

    def _save(self):
        self._file.write_text(json.dumps(self._zooms, ensure_ascii=False, indent=2));

    @staticmethod
    def host_of(url: str) -> str:
        return urlparse(url).netloc;

    def get(self, url: str) -> float:
        return self._zooms.get(self.host_of(url), DEFAULT_ZOOM);

    def set(self, url: str, factor: float):
        host = self.host_of(url);
        if not host:
            return;
        factor = _clamp(factor);
        if abs(factor - DEFAULT_ZOOM) < 1e-6:
            self._zooms.pop(host, None);  # padrão não precisa ser persistido
        else:
            self._zooms[host] = factor;
        self._save();
