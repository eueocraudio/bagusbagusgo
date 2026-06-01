from pathlib import Path;
from PySide6.QtWebEngineCore import QWebEngineProfile;
from .env_config import get_bool;

_EXTENSIONS_DIR = Path(__file__).parent.parent / "data" / "extensions";

_TOGGLES: dict[str, str] = {
    "uBlock0.chromium": "UBLOCK_ENABLED",
};


def load_extensions(profile: QWebEngineProfile):
    if not _EXTENSIONS_DIR.exists():
        return;
    mgr = profile.extensionManager();
    for ext_dir in sorted(_EXTENSIONS_DIR.iterdir()):
        if not ext_dir.is_dir() or not (ext_dir / "manifest.json").exists():
            continue;
        env_key = _TOGGLES.get(ext_dir.name);
        if env_key and not get_bool(env_key, default=True):
            print(f"[extensão] desativada ({env_key}=false): {ext_dir.name}");
            continue;
        mgr.installFinished.connect(
            lambda ok, name=ext_dir.name:
                print(f"[extensão] {'instalada' if ok else 'falhou'}: {name}")
        );
        mgr.installExtension(str(ext_dir));
