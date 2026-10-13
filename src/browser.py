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


def _tem_gpu() -> bool:
    """Há GPU acessível ao Chromium nesta máquina?

    Em qube do Qubes sem GPU atribuída não existe `/dev/dri`. Pedir buffer nativo ali
    (zero-copy, rasterização em GPU, compositing em GPU) enche o log de
    "Failed to get native pixmap due to dma_buf acquisition failure" +
    "Compositor returned null texture" — e a tela vem preta ou picada."""
    dri = Path("/dev/dri");
    return dri.is_dir() and any(dri.glob("renderD*"));


def _apply_chromium_flags():
    flags = [];
    gpu = _tem_gpu();
    if _env.get_bool("WEBGL_FORCE", default=False):
        flags += [
            "--ignore-gpu-blocklist",
            "--enable-webgl",
            "--enable-webgl2",
            "--enable-accelerated-2d-canvas",
        ];
        print(f"[{APP_ID}] WebGL forçado (WEBGL_FORCE=true)");
    elif _env.get_bool("UA_ENGINE_MATCH", default=True):
        # WebGL fica LIGADO: um Chrome 140 sem WebGL não existe, e a ausência desmente o UA
        # que o UA_ENGINE_MATCH anuncia. Só tirar o `--disable-webgl` não basta — sem GPU
        # real o Chromium põe o WebGL na blocklist ("ContextResult::kFatalFailure: WebGL1
        # blocklisted" no log) e `getContext('webgl')` devolve null. Daí o bypass da
        # blocklist + liberação do SwiftShader, que dá WebGL 1 e 2 por software.
        flags += [
            "--ignore-gpu-blocklist",
            "--enable-unsafe-swiftshader",
        ];
        print(f"[{APP_ID}] WebGL por software ligado para casar com a identidade anunciada (UA_ENGINE_MATCH=true)");
    else:
        flags += ["--disable-webgl", "--disable-webgl2"];

    if not gpu:
        # o WebGL por software (SwiftShader) roda, mas o COMPOSITING tem de ser software
        # também: senão o compositor tenta pixmap nativo via dma_buf e falha a cada quadro
        flags += ["--disable-gpu-compositing"];
        # Medido: NÃO dá para trocar o backend de GL por flag aqui. O Qt amarra o GL do
        # Chromium ao contexto dele (vira "ANGLE (Mesa, llvmpipe…)" no
        # UNMASKED_RENDERER_WEBGL, onde o Chrome sem GPU mostra SwiftShader).
        # `--use-angle=swiftshader` e `--use-gl=angle` não mudam nada — não insista.
        # Também não é delator: Chrome real em VM com Mesa reporta a mesma coisa.
        print(f"[{APP_ID}] sem GPU (/dev/dri ausente) — compositing por software");

    if _env.get_bool("MULTITHREAD_ENABLED", default=True):
        cpu = os.cpu_count() or 4;
        raster = _env.get_int("CHROMIUM_RASTER_THREADS", default=min(cpu, 4));
        features = ["ParallelDownloading"];
        if gpu:
            features.append("CanvasOopRasterization");  # rasterização de canvas fora do processo: precisa de GPU
        flags += [
            "--site-per-process",                  # cada site em seu próprio render process (QWebPages em paralelo)
            f"--num-raster-threads={raster}",      # threads de rasterização (escala com CPU)
            f"--enable-features={','.join(features)}",
        ];
        if gpu:
            flags += [
                "--enable-gpu-rasterization",      # rasterização nas threads da GPU
                "--enable-zero-copy",              # upload de texturas sem cópia extra
            ];
        print(f"[{APP_ID}] multithreading Chromium habilitado "
              f"(raster_threads={raster}, cpu={cpu}, gpu={'sim' if gpu else 'não'})");
    else:
        print(f"[{APP_ID}] multithreading Chromium desabilitado (MULTITHREAD_ENABLED=false)");

    # idioma da interface do Chromium: alimenta navigator.language e o locale do Intl.
    # Sem isto o motor reporta "en"/"en-US" enquanto o Accept-Language diz pt-BR.
    from .privacy.user_agent import LANGUAGES;
    flags += [f"--lang={LANGUAGES[0]}"];

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
