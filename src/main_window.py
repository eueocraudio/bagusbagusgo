from pathlib import Path;
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTabWidget,
    QStatusBar, QProgressBar, QSizePolicy,
    QToolButton, QMenu, QMessageBox, QScrollArea,
);
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest, QWebEngineScript, QWebEngineSettings;
from PySide6.QtWebChannel import QWebChannel;
from PySide6.QtCore import QUrl, Qt;
from PySide6.QtGui import QKeySequence, QShortcut;

from .constants import APP_NAME, APP_VERSION, APP_ID;
from .bookmark_manager import BookmarkManager;
from .bookmarks_dialog import ManageBookmarksDialog;
from .history_manager import HistoryManager;
from .history_dialog import HistoryDialog;
from .download_panel import DownloadPanel;
from .click_capture import ClickCapture, CLICK_LISTENER_JS;
from .browser_tab import BrowserTab;
from .user_agent import random_user_agent, navigator_spoof_script;
from .session_manager import SessionManager;
from .ad_blocker import build_ad_block_js;
from .extension_manager import load_extensions;
from .env_config import get_bool;
from .myass.panel import MyAssPanel;


class MainWindow(QMainWindow):
    def __init__(self, base_dir: Path):
        super().__init__();
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}");
        self.setMinimumSize(1024, 700);
        self._downloads_dir = base_dir / "downloads";
        self._downloads_dir.mkdir(parents=True, exist_ok=True);
        self.bookmarks = BookmarkManager(base_dir);
        self.history = HistoryManager(base_dir);
        self.session = SessionManager(base_dir);
        self._build_ui();
        self._build_shortcuts();
        self._connect_downloads();
        self._restore_session();

    def _restore_session(self):
        urls = self.session.load();
        if urls:
            for url in urls:
                self.add_tab(QUrl(url));
        else:
            self.add_tab(QUrl("https://duckduckgo.com"));

    def closeEvent(self, event):
        urls = [
            self.tabs.widget(i).url().toString()
            for i in range(self.tabs.count())
            if isinstance(self.tabs.widget(i), BrowserTab)
        ];
        self.session.save(urls);
        event.accept();

    def _connect_downloads(self):
        profile = QWebEngineProfile.defaultProfile();
        load_extensions(profile);
        profile.settings().setAttribute(QWebEngineSettings.WebAttribute.ForceDarkMode, True);
        ua = random_user_agent();
        if ua:
            profile.setHttpUserAgent(ua);
            print(f"[bagusbagusgo] user-agent: {ua}");
            spoof_script = QWebEngineScript();
            spoof_script.setName("navigator_spoof");
            spoof_script.setSourceCode(navigator_spoof_script(ua));
            spoof_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation);
            spoof_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld);
            profile.scripts().insert(spoof_script);
        ad_skip = QWebEngineScript();
        ad_skip.setName("youtube_ad_skipper");
        ad_skip.setSourceCode("""
(function() {
    if (!window.location.hostname.includes('youtube.com')) return;
    setInterval(function() {
        var skip = document.querySelector(
            '.ytp-skip-ad-button, .ytp-ad-skip-button, .ytp-ad-skip-button-modern'
        );
        if (skip) { skip.click(); return; }
        var overlay = document.querySelector('.ytp-ad-player-overlay, .ad-showing');
        if (overlay) {
            var video = document.querySelector('video');
            if (video && video.duration && !isNaN(video.duration)) {
                video.currentTime = video.duration;
            }
        }
    }, 500);
})();
""");
        ad_skip.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady);
        ad_skip.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld);
        profile.scripts().insert(ad_skip);
        if get_bool("AD_BLOCKER_ENABLED", default=False):
            ad_block = QWebEngineScript();
            ad_block.setName("ad_blocker");
            ad_block.setSourceCode(build_ad_block_js());
            ad_block.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady);
            ad_block.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld);
            profile.scripts().insert(ad_block);
            print("[ad_blocker] habilitado");
        else:
            print("[ad_blocker] desabilitado (AD_BLOCKER_ENABLED=false)");
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
        # --- barra de navegação ---
        nav_bar = QWidget();
        nav_bar.setFixedHeight(36);
        nav_layout = QHBoxLayout(nav_bar);
        nav_layout.setContentsMargins(4, 2, 4, 2);
        nav_layout.setSpacing(2);

        self.btn_back = QPushButton("←");
        self.btn_back.setFixedWidth(32);
        self.btn_back.clicked.connect(lambda: self._current_view().back());
        nav_layout.addWidget(self.btn_back);

        self.btn_forward = QPushButton("→");
        self.btn_forward.setFixedWidth(32);
        self.btn_forward.clicked.connect(lambda: self._current_view().forward());
        nav_layout.addWidget(self.btn_forward);

        self.btn_reload = QPushButton("↻");
        self.btn_reload.setFixedWidth(32);
        self.btn_reload.clicked.connect(self._reload_or_stop);
        nav_layout.addWidget(self.btn_reload);

        self.btn_home = QPushButton("⌂");
        self.btn_home.setFixedWidth(32);
        self.btn_home.clicked.connect(self._go_home);
        nav_layout.addWidget(self.btn_home);

        self.url_bar = QLineEdit();
        self.url_bar.setPlaceholderText("Digite um endereço ou pesquise...");
        self.url_bar.returnPressed.connect(self._navigate_to_url);
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding);
        nav_layout.addWidget(self.url_bar, 1);

        self.btn_bookmark = QPushButton("☆");
        self.btn_bookmark.setFixedWidth(32);
        self.btn_bookmark.setToolTip("Adicionar/remover favorito (Ctrl+D)");
        self.btn_bookmark.clicked.connect(self._toggle_bookmark);
        nav_layout.addWidget(self.btn_bookmark);

        self.btn_manage_bookmarks = QPushButton("★≡");
        self.btn_manage_bookmarks.setFixedWidth(40);
        self.btn_manage_bookmarks.setToolTip("Gerenciar favoritos");
        self.btn_manage_bookmarks.clicked.connect(self._open_manage_dialog);
        nav_layout.addWidget(self.btn_manage_bookmarks);

        self.btn_history = QPushButton("🕐");
        self.btn_history.setFixedWidth(36);
        self.btn_history.setToolTip("Histórico (Ctrl+H)");
        self.btn_history.clicked.connect(self._open_history_dialog);
        nav_layout.addWidget(self.btn_history);

        self.btn_downloads = QPushButton("⬇");
        self.btn_downloads.setFixedWidth(32);
        self.btn_downloads.setToolTip("Downloads (Ctrl+J)");
        self.btn_downloads.clicked.connect(self._toggle_downloads_panel);
        nav_layout.addWidget(self.btn_downloads);

        self.btn_new_tab = QPushButton("+");
        self.btn_new_tab.setFixedWidth(32);
        self.btn_new_tab.clicked.connect(lambda: self.add_tab());
        nav_layout.addWidget(self.btn_new_tab);

        settings_menu = QMenu(self);
        settings_menu.addAction("About", self._open_about);
        self.btn_settings = QToolButton();
        self.btn_settings.setText("⚙");
        self.btn_settings.setFixedWidth(32);
        self.btn_settings.setToolTip("Configurações");
        self.btn_settings.setMenu(settings_menu);
        self.btn_settings.setPopupMode(QToolButton.InstantPopup);
        nav_layout.addWidget(self.btn_settings);

        # --- barra de favoritos ---
        self.bookmarks_bar = QWidget();
        self.bookmarks_bar.setFixedHeight(28);
        self.bookmarks_layout = QHBoxLayout(self.bookmarks_bar);
        self.bookmarks_layout.setContentsMargins(4, 0, 4, 0);
        self.bookmarks_layout.setSpacing(2);
        self.bookmarks_layout.addStretch();
        self._refresh_bookmarks_bar();

        # --- barra de progresso ---
        self.progress_bar = QProgressBar();
        self.progress_bar.setMaximumHeight(4);
        self.progress_bar.setTextVisible(False);

        # --- abas internas (páginas web) ---
        self.tabs = QTabWidget();
        self.tabs.setDocumentMode(True);
        self.tabs.setTabsClosable(True);
        self.tabs.setMovable(True);
        self.tabs.tabCloseRequested.connect(self.close_tab);
        self.tabs.currentChanged.connect(self._on_tab_changed);

        # --- browser widget (tudo junto) ---
        browser_widget = QWidget();
        browser_layout = QVBoxLayout(browser_widget);
        browser_layout.setContentsMargins(0, 0, 0, 0);
        browser_layout.setSpacing(0);
        browser_layout.addWidget(nav_bar);
        browser_layout.addWidget(self.bookmarks_bar);
        browser_layout.addWidget(self.progress_bar);
        browser_layout.addWidget(self.tabs);

        # --- tab externo (envolve o browser inteiro) ---
        self.outer_tabs = QTabWidget();
        self.outer_tabs.addTab(browser_widget, "BagusBagusGo");
        self.outer_tabs.addTab(MyAssPanel(), "MyAss");
        self.outer_tabs.addTab(QWidget(), "Anonymity");
        self.outer_tabs.addTab(QWidget(), "AutoBot");
        self.outer_tabs.addTab(QWidget(), "Downloads");
        self.setCentralWidget(self.outer_tabs);

        # --- painel de downloads ---
        self.download_panel = DownloadPanel(self);
        self.addDockWidget(Qt.BottomDockWidgetArea, self.download_panel);
        self.download_panel.hide();

        self.status_bar = QStatusBar();
        self.setStatusBar(self.status_bar);

    def _refresh_bookmarks_bar(self):
        while self.bookmarks_layout.count():
            item = self.bookmarks_layout.takeAt(0);
            if item.widget():
                item.widget().deleteLater();
        for b in self.bookmarks.all():
            btn = QPushButton(b["title"]);
            btn.setMaximumWidth(160);
            url = b["url"];
            btn.clicked.connect(lambda checked=False, u=url: self._current_view().load(QUrl(u)));
            btn.setToolTip(url);
            self.bookmarks_layout.addWidget(btn);
        self.bookmarks_layout.addStretch();
        self.bookmarks_bar.setVisible(len(self.bookmarks.all()) > 0);

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
        view = self.tabs.widget(index);
        if isinstance(view, BrowserTab):
            view.page().runJavaScript(
                "document.querySelectorAll('video, audio').forEach(function(m) { m.pause(); m.src = ''; });"
            );
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
            f"Sobre o {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p><b>Versão:</b> {APP_VERSION} ({APP_ID})</p>"
            f"<p>Browser desktop construído com <b>Python 3</b> e <b>PySide6</b> (QtWebEngine).</p>"
            f"<p>Motor de busca padrão: DuckDuckGo.</p>",
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
                self.setWindowTitle(f"{title} — {APP_NAME} v{APP_VERSION}");

    def _update_nav_buttons(self, view: BrowserTab):
        history = view.history();
        self.btn_back.setEnabled(history.canGoBack());
        self.btn_forward.setEnabled(history.canGoForward());
