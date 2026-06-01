from pathlib import Path;
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTabWidget, QToolBar,
    QStatusBar, QProgressBar, QSizePolicy,
    QToolButton, QMenu, QMessageBox,
);
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest, QWebEngineScript;
from PySide6.QtWebChannel import QWebChannel;
from PySide6.QtCore import QUrl, Qt;
from PySide6.QtGui import QKeySequence, QShortcut;

from .bookmark_manager import BookmarkManager;
from .bookmarks_dialog import ManageBookmarksDialog;
from .history_manager import HistoryManager;
from .history_dialog import HistoryDialog;
from .download_panel import DownloadPanel;
from .click_capture import ClickCapture, CLICK_LISTENER_JS;
from .browser_tab import BrowserTab;


class MainWindow(QMainWindow):
    def __init__(self, base_dir: Path):
        super().__init__();
        self.setWindowTitle("BagusBagusGo");
        self.setMinimumSize(1024, 700);
        self._downloads_dir = base_dir / "downloads";
        self._downloads_dir.mkdir(parents=True, exist_ok=True);
        self.bookmarks = BookmarkManager(base_dir);
        self.history = HistoryManager(base_dir);
        self._build_ui();
        self._build_shortcuts();
        self._connect_downloads();
        self.add_tab(QUrl("https://duckduckgo.com"));

    def _connect_downloads(self):
        profile = QWebEngineProfile.defaultProfile();
        profile.setDownloadPath(str(self._downloads_dir));
        profile.downloadRequested.connect(self._on_download_requested);
        qwc_script = QWebEngineScript();
        qwc_script.setName("qwebchannel_inject");
        qwc_script.setSourceUrl(QUrl("qrc:///qtwebchannel/qwebchannel.js"));
        qwc_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation);
        qwc_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld);
        profile.scripts().insert(qwc_script);

    def _on_download_requested(self, download: QWebEngineDownloadRequest):
        download.accept();
        self.download_panel.add_download(download);
        self.download_panel.show();
        self.addDockWidget(Qt.BottomDockWidgetArea, self.download_panel);

    def _build_ui(self):
        nav_toolbar = QToolBar("Navegação");
        nav_toolbar.setMovable(False);
        self.addToolBar(nav_toolbar);

        self.btn_back = QPushButton("←");
        self.btn_back.setFixedWidth(32);
        self.btn_back.clicked.connect(lambda: self._current_view().back());
        nav_toolbar.addWidget(self.btn_back);

        self.btn_forward = QPushButton("→");
        self.btn_forward.setFixedWidth(32);
        self.btn_forward.clicked.connect(lambda: self._current_view().forward());
        nav_toolbar.addWidget(self.btn_forward);

        self.btn_reload = QPushButton("↻");
        self.btn_reload.setFixedWidth(32);
        self.btn_reload.clicked.connect(self._reload_or_stop);
        nav_toolbar.addWidget(self.btn_reload);

        self.btn_home = QPushButton("⌂");
        self.btn_home.setFixedWidth(32);
        self.btn_home.clicked.connect(self._go_home);
        nav_toolbar.addWidget(self.btn_home);

        self.url_bar = QLineEdit();
        self.url_bar.setPlaceholderText("Digite um endereço ou pesquise...");
        self.url_bar.returnPressed.connect(self._navigate_to_url);
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding);
        url_container = QWidget();
        url_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred);
        url_container_layout = QHBoxLayout(url_container);
        url_container_layout.setContentsMargins(0, 0, 0, 0);
        url_container_layout.addWidget(self.url_bar, 1);
        nav_toolbar.addWidget(url_container);

        self.btn_bookmark = QPushButton("☆");
        self.btn_bookmark.setFixedWidth(32);
        self.btn_bookmark.setToolTip("Adicionar/remover favorito (Ctrl+D)");
        self.btn_bookmark.clicked.connect(self._toggle_bookmark);
        nav_toolbar.addWidget(self.btn_bookmark);

        self.btn_manage_bookmarks = QPushButton("★≡");
        self.btn_manage_bookmarks.setFixedWidth(40);
        self.btn_manage_bookmarks.setToolTip("Gerenciar favoritos");
        self.btn_manage_bookmarks.clicked.connect(self._open_manage_dialog);
        nav_toolbar.addWidget(self.btn_manage_bookmarks);

        self.btn_history = QPushButton("🕐");
        self.btn_history.setFixedWidth(36);
        self.btn_history.setToolTip("Histórico (Ctrl+H)");
        self.btn_history.clicked.connect(self._open_history_dialog);
        nav_toolbar.addWidget(self.btn_history);

        self.btn_downloads = QPushButton("⬇");
        self.btn_downloads.setFixedWidth(32);
        self.btn_downloads.setToolTip("Downloads (Ctrl+J)");
        self.btn_downloads.clicked.connect(self._toggle_downloads_panel);
        nav_toolbar.addWidget(self.btn_downloads);

        self.btn_new_tab = QPushButton("+");
        self.btn_new_tab.setFixedWidth(32);
        self.btn_new_tab.clicked.connect(lambda: self.add_tab());
        nav_toolbar.addWidget(self.btn_new_tab);

        settings_menu = QMenu(self);
        settings_menu.addAction("About", self._open_about);

        self.btn_settings = QToolButton();
        self.btn_settings.setText("⚙");
        self.btn_settings.setFixedWidth(32);
        self.btn_settings.setToolTip("Configurações");
        self.btn_settings.setMenu(settings_menu);
        self.btn_settings.setPopupMode(QToolButton.InstantPopup);
        nav_toolbar.addWidget(self.btn_settings);

        self.bookmarks_toolbar = QToolBar("Favoritos");
        self.bookmarks_toolbar.setMovable(False);
        self.bookmarks_toolbar.setStyleSheet(
            "QToolBar { spacing: 2px; padding: 2px; }"
            "QPushButton { border: none; padding: 2px 6px; border-radius: 3px; }"
            "QPushButton:hover { background: #e0e0e0; }"
        );
        self.addToolBarBreak(Qt.TopToolBarArea);
        self.addToolBar(Qt.TopToolBarArea, self.bookmarks_toolbar);
        self._refresh_bookmarks_bar();

        self.progress_bar = QProgressBar();
        self.progress_bar.setMaximumHeight(4);
        self.progress_bar.setTextVisible(False);
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: none; background: transparent; }"
            "QProgressBar::chunk { background: #4285f4; }"
        );

        self.tabs = QTabWidget();
        self.tabs.setDocumentMode(True);
        self.tabs.setTabsClosable(True);
        self.tabs.setMovable(True);
        self.tabs.tabCloseRequested.connect(self.close_tab);
        self.tabs.currentChanged.connect(self._on_tab_changed);

        central = QWidget();
        layout = QVBoxLayout(central);
        layout.setContentsMargins(0, 0, 0, 0);
        layout.setSpacing(0);
        layout.addWidget(self.progress_bar);
        layout.addWidget(self.tabs);
        self.setCentralWidget(central);

        self.download_panel = DownloadPanel(self);
        self.addDockWidget(Qt.BottomDockWidgetArea, self.download_panel);
        self.download_panel.hide();

        self.status_bar = QStatusBar();
        self.setStatusBar(self.status_bar);

    def _refresh_bookmarks_bar(self):
        self.bookmarks_toolbar.clear();
        for b in self.bookmarks.all():
            btn = QPushButton(b["title"]);
            btn.setMaximumWidth(160);
            url = b["url"];
            btn.clicked.connect(lambda checked=False, u=url: self._current_view().load(QUrl(u)));
            btn.setToolTip(url);
            self.bookmarks_toolbar.addWidget(btn);
        self.bookmarks_toolbar.setVisible(len(self.bookmarks.all()) > 0);

    def _build_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(lambda: self.add_tab());
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(
            lambda: self.close_tab(self.tabs.currentIndex())
        );
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(
            lambda: self.url_bar.selectAll() or self.url_bar.setFocus()
        );
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self._toggle_bookmark);
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self._open_history_dialog);
        QShortcut(QKeySequence("Ctrl+J"), self).activated.connect(self._toggle_downloads_panel);
        QShortcut(QKeySequence("F5"), self).activated.connect(self._reload_or_stop);
        QShortcut(QKeySequence("Alt+Left"), self).activated.connect(
            lambda: self._current_view().back()
        );
        QShortcut(QKeySequence("Alt+Right"), self).activated.connect(
            lambda: self._current_view().forward()
        );

    def add_tab(self, url: QUrl = None) -> BrowserTab:
        view = BrowserTab(self.add_tab, self.tabs);
        capture = ClickCapture(view);
        channel = QWebChannel(view.page());
        channel.registerObject("capture", capture);
        view.page().setWebChannel(channel);
        view.loadStarted.connect(lambda: self._on_load_started(view));
        view.loadProgress.connect(lambda p: self._on_load_progress(view, p));
        view.loadFinished.connect(lambda ok: self._on_load_finished(view));
        view.urlChanged.connect(lambda u: self._on_url_changed(view, u));
        view.titleChanged.connect(lambda t: self._on_title_changed(view, t));
        view.page().linkHovered.connect(self.status_bar.showMessage);
        index = self.tabs.addTab(view, "Nova aba");
        self.tabs.setCurrentIndex(index);
        view.load(url or QUrl("https://duckduckgo.com"));
        return view;

    def close_tab(self, index: int):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index);
        else:
            self.close();

    def _current_view(self) -> BrowserTab:
        return self.tabs.currentWidget();

    def _navigate_to_url(self):
        text = self.url_bar.text().strip();
        if not text:
            return;
        if "." in text and " " not in text:
            url = QUrl(text if "://" in text else f"https://{text}");
        else:
            url = QUrl(f"https://duckduckgo.com/?q={QUrl.toPercentEncoding(text).data().decode()}");
        self._current_view().load(url);

    def _reload_or_stop(self):
        view = self._current_view();
        if self.btn_reload.text() == "✕":
            view.stop();
        else:
            view.reload();

    def _go_home(self):
        self._current_view().load(QUrl("https://duckduckgo.com"));

    def _toggle_bookmark(self):
        view = self._current_view();
        url = view.url().toString();
        if not url or url == "about:blank":
            return;
        if self.bookmarks.contains(url):
            self.bookmarks.remove(url);
        else:
            self.bookmarks.add(view.title() or url, url);
        self._update_bookmark_button(url);
        self._refresh_bookmarks_bar();

    def _update_bookmark_button(self, url: str):
        self.btn_bookmark.setText("★" if self.bookmarks.contains(url) else "☆");

    def _open_manage_dialog(self):
        dlg = ManageBookmarksDialog(self.bookmarks, self);
        dlg.exec();
        self._refresh_bookmarks_bar();
        self._update_bookmark_button(self._current_view().url().toString());

    def _open_history_dialog(self):
        dlg = HistoryDialog(self.history, self);
        dlg.url_requested.connect(lambda u: self._current_view().load(QUrl(u)));
        dlg.exec();

    def _toggle_downloads_panel(self):
        if self.download_panel.isVisible():
            self.download_panel.hide();
        else:
            self.download_panel.show();
            self.addDockWidget(Qt.BottomDockWidgetArea, self.download_panel);

    def _open_about(self):
        QMessageBox.about(
            self,
            "Sobre o BagusBagusGo",
            "<h2>BagusBagusGo</h2>"
            "<p>Browser desktop construído com <b>Python 3</b> e <b>PySide6</b> (QtWebEngine).</p>"
            "<p>Motor de busca padrão: DuckDuckGo.</p>",
        );

    def _on_tab_changed(self, index: int):
        view = self.tabs.widget(index);
        if view:
            url = view.url().toString();
            self.url_bar.setText(url);
            self._update_nav_buttons(view);
            self._update_bookmark_button(url);

    def _on_load_started(self, view: BrowserTab):
        if view is self._current_view():
            self.btn_reload.setText("✕");
            self.progress_bar.setValue(0);
            self.progress_bar.show();

    def _on_load_progress(self, view: BrowserTab, progress: int):
        if view is self._current_view():
            self.progress_bar.setValue(progress);

    def _on_load_finished(self, view: BrowserTab):
        url = view.url().toString();
        if url and url != "about:blank":
            self.history.record(view.title() or url, url);
        view.page().runJavaScript(CLICK_LISTENER_JS);
        if "google.com" in url:
            view.page().runJavaScript("window.location.href = 'https://duckduckgo.com';");
        if view is self._current_view():
            self.btn_reload.setText("↻");
            self.progress_bar.hide();
            self._update_nav_buttons(view);

    def _on_url_changed(self, view: BrowserTab, url: QUrl):
        if view is self._current_view():
            url_str = url.toString();
            self.url_bar.setText(url_str);
            self._update_bookmark_button(url_str);

    def _on_title_changed(self, view: BrowserTab, title: str):
        index = self.tabs.indexOf(view);
        if index >= 0:
            short = title[:20] + "…" if len(title) > 20 else title;
            self.tabs.setTabText(index, short or "Nova aba");
            if view is self._current_view():
                self.setWindowTitle(f"{title} — BagusBagusGo");

    def _update_nav_buttons(self, view: BrowserTab):
        history = view.history();
        self.btn_back.setEnabled(history.canGoBack());
        self.btn_forward.setEnabled(history.canGoForward());
