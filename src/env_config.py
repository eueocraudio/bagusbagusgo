import os;
from pathlib import Path;

_PROJECT_DIR = Path(__file__).parent.parent;
_INSTALL_DIR = Path.home() / ".local" / "bin" / "bagus";


def _load_file(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip();
        if not line or line.startswith("#") or "=" not in line:
            continue;
        key, _, value = line.partition("=");
        os.environ[key.strip()] = value.strip();


def load(base_dir: Path = None):
    sources = [
        _PROJECT_DIR / ".env",      # nível 1 — diretório do projeto/source
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
