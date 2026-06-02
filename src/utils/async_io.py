"""Gravador de JSON assíncrono.

Tira a escrita em disco da thread de UI. Mantém uma única thread dedicada que
coalesce gravações por caminho (a última vence) e escreve de forma atômica
(arquivo temporário + replace), evitando corrupção em caso de crash.

A serialização (json.dumps) acontece de forma síncrona na thread chamadora, o que
fixa um snapshot consistente dos dados; só a I/O de disco é offloaded.

Uso:
    from ..utils.async_io import writer;
    writer().write(path, dados);   # enfileira; retorna imediatamente
    writer().flush();              # bloqueia até esvaziar (chamar no closeEvent)
"""
import json;
import threading;
from pathlib import Path;


class AsyncJsonWriter:
    def __init__(self):
        self._pending: dict[str, str] = {};
        self._lock = threading.Lock();
        self._wake = threading.Event();
        self._idle = threading.Event();
        self._idle.set();
        self._thread = threading.Thread(target=self._loop, name="bbgo-json-writer", daemon=True);
        self._thread.start();

    def write(self, path, data):
        self.write_text(path, json.dumps(data, ensure_ascii=False, indent=2));

    def write_text(self, path, text: str):
        with self._lock:
            self._pending[str(path)] = text;
            self._idle.clear();
        self._wake.set();

    def flush(self, timeout: float = 5.0) -> bool:
        self._wake.set();
        return self._idle.wait(timeout);

    def _loop(self):
        while True:
            self._wake.wait();
            self._wake.clear();
            with self._lock:
                batch = self._pending;
                self._pending = {};
            for path_str, text in batch.items():
                self._write_one(path_str, text);
            with self._lock:
                if not self._pending:
                    self._idle.set();

    @staticmethod
    def _write_one(path_str: str, text: str):
        try:
            path = Path(path_str);
            path.parent.mkdir(parents=True, exist_ok=True);
            tmp = path.with_name(path.name + ".tmp");
            tmp.write_text(text, encoding="utf-8");
            tmp.replace(path);
        except Exception as e:
            print(f"[async_io] falha ao gravar {path_str}: {e}");


_writer: AsyncJsonWriter = None;


def writer() -> AsyncJsonWriter:
    global _writer;
    if _writer is None:
        _writer = AsyncJsonWriter();
    return _writer;
