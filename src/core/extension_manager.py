from pathlib import Path;
from PySide6.QtWebEngineCore import QWebEngineProfile;
from ..settings.env_config import get_bool;

_ROOT = Path(__file__).parent.parent.parent;
_EXTENSIONS_DIR = _ROOT / "data" / "extensions";

_TOGGLES: dict[str, str] = {
    "uBlock0.chromium": "UBLOCK_ENABLED",
};


def load_extensions(profile: QWebEngineProfile):
    if not _EXTENSIONS_DIR.exists():
        return;
    mgr = profile.extensionManager();
    to_install: list[str] = [];
    for ext_dir in sorted(_EXTENSIONS_DIR.iterdir()):
        if not ext_dir.is_dir() or not (ext_dir / "manifest.json").exists():
            continue;
        env_key = _TOGGLES.get(ext_dir.name);
        if env_key and not get_bool(env_key, default=True):
            print(f"[extensão] desativada ({env_key}=false): {ext_dir.name}");
            continue;
        to_install.append(ext_dir.name);
    if not to_install:
        return;
    # instala uma de cada vez: installFinished(ok) não diz qual extensão terminou,
    # então só iniciamos a próxima depois da anterior — o nome logado sempre bate
    # com o resultado, independente da ordem de conclusão do Chromium
    index = [0];
    def _install_next():
        if index[0] >= len(to_install):
            mgr.installFinished.disconnect(_on_installed);
            return;
        mgr.installExtension(str(_EXTENSIONS_DIR / to_install[index[0]]));
    def _on_installed(ok):
        name = to_install[index[0]];
        print(f"[extensão] {'instalada' if ok else 'falhou'}: {name}");
        index[0] += 1;
        _install_next();
    mgr.installFinished.connect(_on_installed);
    _install_next();
