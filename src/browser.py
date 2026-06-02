import sys;
import os;
import tempfile;
from pathlib import Path;
from PySide6.QtWidgets import QApplication;
from .settings import env_config as _env;
from .main_window import MainWindow;
from .utils.theme import DARK_STYLESHEET;
from .utils.constants import APP_NAME, APP_VERSION, APP_ID;
from .utils import logger as _logger_mod;


def _apply_chromium_flags():
    flags = [];
    if _env.get_bool("WEBGL_FORCE", default=False):
        flags += [
            "--ignore-gpu-blocklist",
            "--enable-webgl",
            "--enable-webgl2",
            "--enable-accelerated-2d-canvas",
        ];
        print(f"[{APP_ID}] WebGL forçado (WEBGL_FORCE=true)");
    else:
        flags += ["--disable-webgl", "--disable-webgl2"];

    if _env.get_bool("MULTITHREAD_ENABLED", default=True):
        cpu = os.cpu_count() or 4;
        raster = _env.get_int("CHROMIUM_RASTER_THREADS", default=min(cpu, 4));
        features = ["ParallelDownloading", "CanvasOopRasterization"];
        flags += [
            "--site-per-process",                  # cada site em seu próprio render process (QWebPages em paralelo)
            "--enable-gpu-rasterization",          # rasterização nas threads da GPU
            "--enable-zero-copy",                  # upload de texturas sem cópia extra
            f"--num-raster-threads={raster}",      # threads de rasterização (escala com CPU)
            f"--enable-features={','.join(features)}",
        ];
        print(f"[{APP_ID}] multithreading Chromium habilitado (raster_threads={raster}, cpu={cpu})");
    else:
        print(f"[{APP_ID}] multithreading Chromium desabilitado (MULTITHREAD_ENABLED=false)");

    existing = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "");
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (existing + " " + " ".join(flags)).strip();


def main(args: list[str] = None):
    if args is None:
        args = sys.argv;
    if len(args) > 1:
        base_dir = Path(args[1]).resolve();
        base_dir.mkdir(parents=True, exist_ok=True);
    else:
        base_dir = Path(tempfile.mkdtemp(prefix="bagusbagusgo_", dir="/tmp"));
    _env.load(base_dir);
    _apply_chromium_flags();
    _logger_mod.setup(base_dir);
    print(f"[{APP_ID} v{APP_VERSION}] diretório de dados: {base_dir}");
    app = QApplication(args);
    app.setApplicationName(APP_NAME);
    app.setApplicationVersion(APP_VERSION);
    app.setStyleSheet(DARK_STYLESHEET);
    try:
        zoom = int(os.environ.get("ZOOM", "1"));
    except ValueError:
        zoom = 1;
    if zoom > 0:
        font = app.font();
        font.setPointSize(font.pointSize() + zoom);
        app.setFont(font);
        print(f"[{APP_ID}] ZOOM={zoom} — fonte: {font.pointSize()}pt");
    window = MainWindow(base_dir);
    # redimensiona para a área útil da tela antes de exibir: garante janela cheia mesmo
    # quando o gerenciador de janelas ignora o pedido de maximizar
    screen = app.primaryScreen();
    if screen is not None:
        window.setGeometry(screen.availableGeometry());
    window.showMaximized();
    sys.exit(app.exec());


if __name__ == "__main__":
    main(sys.argv);
