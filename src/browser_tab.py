from typing import Callable;
from PySide6.QtWebEngineWidgets import QWebEngineView;
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile;


class BrowserTab(QWebEngineView):
    def __init__(self, add_tab_callback: Callable, profile: QWebEngineProfile, parent=None):
        super().__init__(parent);
        self._add_tab = add_tab_callback;
        self.setPage(QWebEnginePage(profile, self));

    def createWindow(self, window_type):
        return self._add_tab();
