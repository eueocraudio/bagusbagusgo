import os;
from pathlib import Path;

_ROOT = Path(__file__).parent.parent.parent;
_INSTALL_DIR = Path.home() / ".local" / "bin" / "bagus";
_SHELL_VARS  = frozenset(os.environ.keys());  # vars set before any .env is loaded


def _load_file(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip();
        if not line or line.startswith("#") or "=" not in line:
            continue;
        key, _, value = line.partition("=");
        key = key.strip();
        if key not in _SHELL_VARS:            # shell-exported vars always win
            os.environ[key] = value.strip();


def load(base_dir: Path = None):
    sources = [
        _ROOT / ".env",             # nível 1 — diretório do projeto/source
        Path.home() / ".env",       # nível 2 — usuário global
        _INSTALL_DIR / ".env",      # nível 3 — instalação
    ];
    if base_dir:
        sources.append(Path(base_dir) / ".env");  # nível 4 — perfil (maior prioridade)
    for path in sources:
        if path.exists():
            _load_file(path);
            print(f"[env] carregado: {path}");


def get_bool(key: str, default: bool = False) -> bool:
    return os.environ.get(key, str(default)).strip().lower() in ("true", "1", "yes");


def get_str(key: str, default: str = "") -> str:
    val = os.environ.get(key, "").strip();
    return val if val else default;


def get_int(key: str, default: int = 0) -> int:
    try:
        return int(os.environ.get(key, "").strip());
    except (ValueError, TypeError):
        return default;
