"""Executor assíncrono baseado em QThreadPool.

Permite rodar funções bloqueantes (rede, disco, parsing) fora da thread de UI
e receber o resultado de volta na thread de UI via signals (conexões enfileiradas
automaticamente, pois os signals vivem no objeto criado na thread chamadora).

Uso:
    from ..utils.tasks import run_async;
    run_async(minha_funcao, arg1, arg2,
              on_result=lambda r: ...,   # roda na thread de UI
              on_error=lambda msg: ...); # roda na thread de UI
"""
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot;

# mantém referência aos workers ativos até 'finished' ser entregue na thread de UI,
# evitando que o QObject de signals seja coletado antes dos slots enfileirados rodarem.
_active: set = set();


class WorkerSignals(QObject):
    result   = Signal(object);
    error    = Signal(str);
    finished = Signal();


class _Worker(QRunnable):
    def __init__(self, fn, args, kwargs):
        super().__init__();
        self._fn = fn;
        self._args = args;
        self._kwargs = kwargs;
        self.signals = WorkerSignals();

    @Slot()
    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs);
        except Exception as e:
            self.signals.error.emit(str(e));
        else:
            self.signals.result.emit(result);
        finally:
            self.signals.finished.emit();


def pool() -> QThreadPool:
    return QThreadPool.globalInstance();


def run_async(fn, *args, on_result=None, on_error=None, on_finished=None, **kwargs) -> _Worker:
    worker = _Worker(fn, args, kwargs);
    _active.add(worker);
    if on_result is not None:
        worker.signals.result.connect(on_result);
    if on_error is not None:
        worker.signals.error.connect(on_error);
    if on_finished is not None:
        worker.signals.finished.connect(on_finished);
    worker.signals.finished.connect(lambda w=worker: _active.discard(w));
    pool().start(worker);
    return worker;
