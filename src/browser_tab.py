from typing import Callable;
from PySide6.QtWebEngineWidgets import QWebEngineView;
from PySide6.QtWebEngineCore import QWebEnginePage;


class BrowserTab(QWebEngineView):
    def __init__(self, add_tab_callback: Callable, parent=None):
        super().__init__(parent);
        self._add_tab = add_tab_callback;

    def createWindow(self, window_type):
        return self._add_tab();
