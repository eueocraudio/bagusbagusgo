from pathlib import Path;
from PySide6.QtWebEngineCore import QWebEngineProfile;

_EXTENSIONS_DIR = Path(__file__).parent.parent / "data" / "extensions";


def load_extensions(profile: QWebEngineProfile):
    if not _EXTENSIONS_DIR.exists():
        return;
    mgr = profile.extensionManager();
    for ext_dir in sorted(_EXTENSIONS_DIR.iterdir()):
        if not ext_dir.is_dir() or not (ext_dir / "manifest.json").exists():
            continue;
        mgr.installFinished.connect(
            lambda ok, name=ext_dir.name:
                print(f"[extensão] {'instalada' if ok else 'falhou'}: {name}")
        );
        mgr.installExtension(str(ext_dir));
