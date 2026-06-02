import json;
from pathlib import Path;
from ..utils.async_io import writer;

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
        writer().write(self._file, self._zooms);

    @staticmethod
    def _key(url: str) -> str:
        # zoom é por página (URL), ignorando o fragmento (#âncora) — mesma página
        return url.split("#", 1)[0];

    def get(self, url: str) -> float:
        return self._zooms.get(self._key(url), DEFAULT_ZOOM);

    def set(self, url: str, factor: float):
        key = self._key(url);
        if not key or key == "about:blank":
            return;
        factor = _clamp(factor);
        if abs(factor - DEFAULT_ZOOM) < 1e-6:
            self._zooms.pop(key, None);  # padrão não precisa ser persistido
        else:
            self._zooms[key] = factor;
        self._save();
