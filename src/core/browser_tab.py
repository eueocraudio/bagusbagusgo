import logging;
from typing import Callable;
from PySide6.QtCore import QEvent, Qt;
from PySide6.QtWebEngineWidgets import QWebEngineView;
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile;
from ..utils import logger as _logger_mod;

_JS_LEVELS = {
    QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel:    logging.INFO,
    QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: logging.WARNING,
    QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:   logging.ERROR,
};


class LoggingWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        py_level = _JS_LEVELS.get(level, logging.INFO);
        _logger_mod.web_logger().log(py_level, f"{message}  ({source_id}:{line_number})");


class BrowserTab(QWebEngineView):
    def __init__(self, add_tab_callback: Callable, profile: QWebEngineProfile, on_ctrl_wheel: Callable = None, parent=None):
        super().__init__(parent);
        self._add_tab = add_tab_callback;
        self._on_ctrl_wheel = on_ctrl_wheel;
        self.setPage(LoggingWebEnginePage(profile, self));

    def createWindow(self, window_type):
        return self._add_tab();

    def childEvent(self, event):
        # o QWebEngineView delega input ao widget interno de renderização, que é
        # adicionado como filho; instalamos o filtro nele (escopo estreito e seguro —
        # filtrar a QApplication inteira causa segfault na init do WebEngine)
        if event.type() == QEvent.Type.ChildAdded:
            child = event.child();
            if child is not None and child.isWidgetType():
                child.installEventFilter(self);
        super().childEvent(event);

    def eventFilter(self, obj, event):
        if (self._on_ctrl_wheel is not None
                and event.type() == QEvent.Type.Wheel
                and (event.modifiers() & Qt.KeyboardModifier.ControlModifier)):
            self._on_ctrl_wheel(event.angleDelta().y());
            return True;  # consome o evento para a página não rolar junto
        return super().eventFilter(obj, event);
