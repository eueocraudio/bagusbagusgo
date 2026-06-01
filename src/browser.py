import sys;
import tempfile;
from pathlib import Path;
from PySide6.QtWidgets import QApplication;
from .main_window import MainWindow;


def main():
    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1]).resolve();
        base_dir.mkdir(parents=True, exist_ok=True);
    else:
        base_dir = Path(tempfile.mkdtemp(prefix="bagusbagusgo_", dir="/tmp"));
    print(f"[bagusbagusgo] diretório de dados: {base_dir}");
    app = QApplication(sys.argv);
    app.setApplicationName("BagusBagusGo");
    window = MainWindow(base_dir);
    window.show();
    sys.exit(app.exec());


if __name__ == "__main__":
    main();
