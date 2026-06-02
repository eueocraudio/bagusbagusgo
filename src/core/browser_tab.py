import logging;
from typing import Callable;
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
    def __init__(self, add_tab_callback: Callable, profile: QWebEngineProfile, parent=None):
        super().__init__(parent);
        self._add_tab = add_tab_callback;
        self.setPage(LoggingWebEnginePage(profile, self));

    def createWindow(self, window_type):
        return self._add_tab();
