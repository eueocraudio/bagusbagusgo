import sys;
import tempfile;
from pathlib import Path;
from PySide6.QtWidgets import QApplication;
from .main_window import MainWindow;
from .theme import DARK_STYLESHEET;
from .constants import APP_NAME, APP_VERSION, APP_ID;


def main(args: list[str] = None):
    if args is None:
        args = sys.argv;
    if len(args) > 1:
        base_dir = Path(args[1]).resolve();
        base_dir.mkdir(parents=True, exist_ok=True);
    else:
        base_dir = Path(tempfile.mkdtemp(prefix="bagusbagusgo_", dir="/tmp"));
    print(f"[{APP_ID} v{APP_VERSION}] diretório de dados: {base_dir}");
    app = QApplication(args);
    app.setApplicationName(APP_NAME);
    app.setApplicationVersion(APP_VERSION);
    app.setStyleSheet(DARK_STYLESHEET);
    window = MainWindow(base_dir);
    window.show();
    sys.exit(app.exec());


if __name__ == "__main__":
    main(sys.argv);
