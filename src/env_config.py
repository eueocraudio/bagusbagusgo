import os;
from pathlib import Path;

_ENV_FILE = Path(__file__).parent.parent / ".env";


def load():
    if not _ENV_FILE.exists():
        return;
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip();
        if not line or line.startswith("#") or "=" not in line:
            continue;
        key, _, value = line.partition("=");
        os.environ.setdefault(key.strip(), value.strip());


def get_bool(key: str, default: bool = False) -> bool:
    return os.environ.get(key, str(default)).strip().lower() in ("true", "1", "yes");
