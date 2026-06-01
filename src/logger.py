import sys;
import logging;
from pathlib import Path;
from datetime import datetime;


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
    log_file = base_dir / "bagusbagusgo.log";
    base_dir.mkdir(parents=True, exist_ok=True);

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.__stdout__),
        ],
    );

    logger = logging.getLogger("bbgo");

    sys.stdout = _StreamToLogger(logger, logging.INFO);
    sys.stderr = _StreamToLogger(logger, logging.ERROR);

    logger.info(f"Log iniciado — {log_file}");
    return logger;
