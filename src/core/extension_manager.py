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
    counter = [0];
    def _on_installed(ok):
        name = to_install[counter[0]] if counter[0] < len(to_install) else "?";
        print(f"[extensão] {'instalada' if ok else 'falhou'}: {name}");
        counter[0] += 1;
    mgr.installFinished.connect(_on_installed);
    for name in to_install:
        mgr.installExtension(str(_EXTENSIONS_DIR / name));
