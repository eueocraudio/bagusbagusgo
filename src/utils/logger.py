import sys;
import logging;
from pathlib import Path;

_FORMAT  = "%(asctime)s  %(levelname)-8s  %(message)s";
_DATEFMT = "%Y-%m-%d %H:%M:%S";

_web_logger = None;  # logger de conteúdo web (console JS, CORS, etc.) — setado em setup()


class _StreamToLogger:
    def __init__(self, logger: logging.Logger, level: int):
        self._logger = logger;
        self._level = level;
        self._buf = "";

    def write(self, msg: str):
        self._buf += msg;
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1);
            if line.rstrip():
                self._logger.log(self._level, line.rstrip());

    def flush(self):
        if self._buf.rstrip():
            self._logger.log(self._level, self._buf.rstrip());
            self._buf = "";

    def fileno(self):
        raise OSError("logger stream has no fileno");


def setup(base_dir: Path) -> logging.Logger:
    global _web_logger;
    base_dir.mkdir(parents=True, exist_ok=True);
    log_file = base_dir / "bagusbagusgo.log";
    web_file = base_dir / "webengine.log";

    # logger do app: stdout/stderr + terminal (handlers no root via basicConfig)
    logging.basicConfig(
        level=logging.DEBUG,
        format=_FORMAT,
        datefmt=_DATEFMT,
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.__stdout__),
        ],
    );
    logger = logging.getLogger("bbgo");

    # logger de conteúdo web: arquivo próprio, isolado do log do app e do terminal
    _web_logger = logging.getLogger("bbgo.web");
    _web_logger.setLevel(logging.DEBUG);
    _web_logger.propagate = False;
    web_handler = logging.FileHandler(web_file, encoding="utf-8");
    web_handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATEFMT));
    _web_logger.addHandler(web_handler);

    sys.stdout = _StreamToLogger(logger, logging.INFO);
    sys.stderr = _StreamToLogger(logger, logging.ERROR);

    logger.info(f"Log iniciado — {log_file}");
    _web_logger.info(f"Log de WebEngine iniciado — {web_file}");
    return logger;


def web_logger() -> logging.Logger:
    return _web_logger if _web_logger is not None else logging.getLogger("bbgo.web");
