import sys;
import json;
import os;
import subprocess;
from datetime import datetime, date, timedelta;
from pathlib import Path;
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton, QTabWidget,
    QToolBar, QStatusBar, QProgressBar, QDialog,
    QListWidget, QListWidgetItem, QDialogButtonBox,
    QLabel, QInputDialog, QMessageBox, QDockWidget,
    QScrollArea, QFrame, QSizePolicy,
);
from PySide6.QtWebEngineWidgets import QWebEngineView;
from PySide6.QtWebEngineCore import (
    QWebEnginePage, QWebEngineProfile, QWebEngineDownloadRequest, QWebEngineScript,
);
from PySide6.QtWebChannel import QWebChannel;
from PySide6.QtCore import QUrl, Qt, Signal, QTimer, QObject, Slot;
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QAction;


BOOKMARKS_FILE = Path.home() / ".config" / "webcraudiobot" / "bookmarks.json";
HISTORY_FILE   = Path.home() / ".config" / "webcraudiobot" / "history.json";
DOWNLOADS_DIR  = Path.home() / "Downloads";
HISTORY_MAX    = 5000;


# ---------------------------------------------------------------------------
# Favoritos
# ---------------------------------------------------------------------------

class BookmarkManager:
    def __init__(self):
        BOOKMARKS_FILE.parent.mkdir(parents=True, exist_ok=True);
        self._bookmarks: list[dict] = self._load();

    def _load(self) -> list[dict]:
        if BOOKMARKS_FILE.exists():
            try:
                return json.loads(BOOKMARKS_FILE.read_text());
            except Exception:
                return [];
        return [];

    def _save(self):
        BOOKMARKS_FILE.write_text(json.dumps(self._bookmarks, ensure_ascii=False, indent=2));

    def all(self) -> list[dict]:
        return list(self._bookmarks);

    def contains(self, url: str) -> bool:
        return any(b["url"] == url for b in self._bookmarks);

    def add(self, title: str, url: str):
        if not self.contains(url):
            self._bookmarks.append({"title": title, "url": url});
            self._save();

    def remove(self, url: str):
        self._bookmarks = [b for b in self._bookmarks if b["url"] != url];
        self._save();

    def rename(self, url: str, new_title: str):
        for b in self._bookmarks:
            if b["url"] == url:
                b["title"] = new_title;
                break;
        self._save();


class ManageBookmarksDialog(QDialog):
    def __init__(self, manager: BookmarkManager, parent=None):
        super().__init__(parent);
        self.manager = manager;
        self.setWindowTitle("Gerenciar favoritos");
        self.setMinimumSize(480, 360);
        self._build_ui();
        self._populate();

    def _build_ui(self):
        layout = QVBoxLayout(self);
        self.list_widget = QListWidget();
        self.list_widget.itemDoubleClicked.connect(self._rename);
        layout.addWidget(self.list_widget);

        btn_row = QHBoxLayout();
        self.btn_rename = QPushButton("Renomear");
        self.btn_rename.clicked.connect(self._rename);
        self.btn_remove = QPushButton("Remover");
        self.btn_remove.clicked.connect(self._remove);
        btn_row.addWidget(self.btn_rename);
        btn_row.addWidget(self.btn_remove);
        btn_row.addStretch();
        layout.addLayout(btn_row);

        buttons = QDialogButtonBox(QDialogButtonBox.Close);
        buttons.rejected.connect(self.accept);
        layout.addWidget(buttons);

    def _populate(self):
        self.list_widget.clear();
        for b in self.manager.all():
            item = QListWidgetItem(f"{b['title']}  —  {b['url']}");
            item.setData(Qt.UserRole, b["url"]);
            self.list_widget.addItem(item);

    def _rename(self):
        item = self.list_widget.currentItem();
        if not item:
            return;
        url = item.data(Qt.UserRole);
        current_title = next(b["title"] for b in self.manager.all() if b["url"] == url);
        new_title, ok = QInputDialog.getText(self, "Renomear", "Novo nome:", text=current_title);
        if ok and new_title.strip():
            self.manager.rename(url, new_title.strip());
            self._populate();

    def _remove(self):
        item = self.list_widget.currentItem();
        if not item:
            return;
        self.manager.remove(item.data(Qt.UserRole));
        self._populate();


# ---------------------------------------------------------------------------
# Histórico
# ---------------------------------------------------------------------------

class HistoryManager:
    def __init__(self):
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True);
        self._entries: list[dict] = self._load();

    def _load(self) -> list[dict]:
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text());
            except Exception:
                return [];
        return [];

    def _save(self):
        HISTORY_FILE.write_text(json.dumps(self._entries, ensure_ascii=False, indent=2));

    def record(self, title: str, url: str):
        if not url or url == "about:blank":
            return;
        self._entries.append({
            "title": title or url,
            "url": url,
            "visited_at": datetime.now().isoformat(timespec="seconds"),
        });
        if len(self._entries) > HISTORY_MAX:
            self._entries = self._entries[-HISTORY_MAX:];
        self._save();

    def all(self) -> list[dict]:
        return list(reversed(self._entries));

    def search(self, query: str) -> list[dict]:
        q = query.lower();
        return [e for e in self.all() if q in e["title"].lower() or q in e["url"].lower()];

    def remove(self, index_in_reversed: int):
        real = len(self._entries) - 1 - index_in_reversed;
        if 0 <= real < len(self._entries):
            self._entries.pop(real);
            self._save();

    def clear(self):
        self._entries = [];
        self._save();


class HistoryDialog(QDialog):
    url_requested = Signal(str);

    def __init__(self, manager: HistoryManager, parent=None):
        super().__init__(parent);
        self.manager = manager;
        self.setWindowTitle("Histórico de navegação");
        self.setMinimumSize(560, 460);
        self._build_ui();
        self._populate("");

    def _build_ui(self):
        layout = QVBoxLayout(self);

        self.search_bar = QLineEdit();
        self.search_bar.setPlaceholderText("Pesquisar no histórico...");
        self.search_bar.textChanged.connect(self._populate);
        layout.addWidget(self.search_bar);

        self.list_widget = QListWidget();
        self.list_widget.itemDoubleClicked.connect(self._open_url);
        layout.addWidget(self.list_widget);

        btn_row = QHBoxLayout();
        self.btn_open = QPushButton("Abrir");
        self.btn_open.clicked.connect(self._open_url);
        self.btn_remove = QPushButton("Remover entrada");
        self.btn_remove.clicked.connect(self._remove_entry);
        self.btn_clear = QPushButton("Limpar tudo");
        self.btn_clear.clicked.connect(self._clear_all);
        btn_row.addWidget(self.btn_open);
        btn_row.addWidget(self.btn_remove);
        btn_row.addStretch();
        btn_row.addWidget(self.btn_clear);
        layout.addLayout(btn_row);

        buttons = QDialogButtonBox(QDialogButtonBox.Close);
        buttons.rejected.connect(self.accept);
        layout.addWidget(buttons);

    def _populate(self, query: str = ""):
        self.list_widget.clear();
        entries = self.manager.search(query) if query else self.manager.all();
        last_group = None;
        today = date.today();
        yesterday = today - timedelta(days=1);
        for idx, entry in enumerate(entries):
            visited = datetime.fromisoformat(entry["visited_at"]).date();
            if visited == today:
                group = "Hoje";
            elif visited == yesterday:
                group = "Ontem";
            else:
                group = visited.strftime("%d/%m/%Y");
            if group != last_group:
                header = QListWidgetItem(f"  {group}");
                header.setFlags(Qt.NoItemFlags);
                header.setBackground(self.palette().alternateBase());
                self.list_widget.addItem(header);
                last_group = group;
            visited_dt = datetime.fromisoformat(entry["visited_at"]);
            item = QListWidgetItem(f"  {visited_dt.strftime('%H:%M')}  {entry['title']}  —  {entry['url']}");
            item.setData(Qt.UserRole, (idx, entry["url"]));
            self.list_widget.addItem(item);

    def _open_url(self):
        item = self.list_widget.currentItem();
        if not item or not item.data(Qt.UserRole):
            return;
        _, url = item.data(Qt.UserRole);
        self.url_requested.emit(url);
        self.accept();

    def _remove_entry(self):
        item = self.list_widget.currentItem();
        if not item or not item.data(Qt.UserRole):
            return;
        idx, _ = item.data(Qt.UserRole);
        self.manager.remove(idx);
        self._populate(self.search_bar.text());

    def _clear_all(self):
        resp = QMessageBox.question(
            self, "Limpar histórico",
            "Apagar todo o histórico de navegação?",
            QMessageBox.Yes | QMessageBox.No,
        );
        if resp == QMessageBox.Yes:
            self.manager.clear();
            self._populate(self.search_bar.text());


# ---------------------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------------------

def _fmt_size(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}";
        b /= 1024;
    return f"{b:.1f} TB";


class DownloadItemWidget(QFrame):
    def __init__(self, download: QWebEngineDownloadRequest, parent=None):
        super().__init__(parent);
        self.download = download;
        self._last_bytes = 0;
        self._last_tick_bytes = 0;
        self._speed = 0;
        self.setFrameShape(QFrame.StyledPanel);
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed);
        self._build_ui();
        self._connect_signals();
        self._speed_timer = QTimer(self);
        self._speed_timer.setInterval(1000);
        self._speed_timer.timeout.connect(self._update_speed);
        self._speed_timer.start();

    def _build_ui(self):
        layout = QVBoxLayout(self);
        layout.setContentsMargins(6, 4, 6, 4);
        layout.setSpacing(2);

        top_row = QHBoxLayout();
        filename = Path(self.download.downloadFileName()).name;
        self.lbl_name = QLabel(filename);
        self.lbl_name.setStyleSheet("font-weight: bold;");
        self.lbl_name.setToolTip(str(self.download.downloadDirectory()) + "/" + filename);
        top_row.addWidget(self.lbl_name, 1);

        self.btn_cancel = QPushButton("Cancelar");
        self.btn_cancel.setFixedWidth(72);
        self.btn_cancel.clicked.connect(self.download.cancel);
        top_row.addWidget(self.btn_cancel);

        self.btn_open = QPushButton("Abrir");
        self.btn_open.setFixedWidth(56);
        self.btn_open.setVisible(False);
        self.btn_open.clicked.connect(self._open_file);
        top_row.addWidget(self.btn_open);

        self.btn_folder = QPushButton("Pasta");
        self.btn_folder.setFixedWidth(56);
        self.btn_folder.setVisible(False);
        self.btn_folder.clicked.connect(self._open_folder);
        top_row.addWidget(self.btn_folder);

        layout.addLayout(top_row);

        self.progress = QProgressBar();
        self.progress.setMaximumHeight(6);
        self.progress.setTextVisible(False);
        self.progress.setRange(0, 100);
        layout.addWidget(self.progress);

        self.lbl_status = QLabel("Aguardando...");
        self.lbl_status.setStyleSheet("color: grey; font-size: 11px;");
        layout.addWidget(self.lbl_status);

    def _connect_signals(self):
        self.download.receivedBytesChanged.connect(self._on_progress);
        self.download.stateChanged.connect(self._on_state_changed);

    def _on_progress(self):
        received = self.download.receivedBytes();
        total = self.download.totalBytes();
        self._last_bytes = received;
        if total > 0:
            self.progress.setValue(int(received * 100 / total));
        else:
            self.progress.setRange(0, 0);
        speed_str = f"{_fmt_size(self._speed)}/s" if self._speed > 0 else "";
        total_str = f" de {_fmt_size(total)}" if total > 0 else "";
        self.lbl_status.setText(f"{_fmt_size(received)}{total_str}  {speed_str}");

    def _update_speed(self):
        self._speed = max(0, self._last_bytes - self._last_tick_bytes);
        self._last_tick_bytes = self._last_bytes;

    def _on_state_changed(self, state):
        self._speed_timer.stop();
        self.btn_cancel.setVisible(False);
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self.progress.setRange(0, 100);
            self.progress.setValue(100);
            self.lbl_status.setText(f"Concluído  —  {_fmt_size(self.download.receivedBytes())}");
            self.lbl_status.setStyleSheet("color: green; font-size: 11px;");
            self.btn_open.setVisible(True);
            self.btn_folder.setVisible(True);
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            self.progress.setRange(0, 100);
            self.progress.setValue(0);
            self.lbl_status.setText("Cancelado");
            self.lbl_status.setStyleSheet("color: orange; font-size: 11px;");
            self.btn_folder.setVisible(True);
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            self.lbl_status.setText("Erro no download");
            self.lbl_status.setStyleSheet("color: red; font-size: 11px;");
            self.btn_folder.setVisible(True);

    def _open_file(self):
        path = str(Path(self.download.downloadDirectory()) / self.download.downloadFileName());
        if sys.platform == "win32":
            os.startfile(path);
        else:
            subprocess.Popen(["xdg-open", path]);

    def _open_folder(self):
        subprocess.Popen(["xdg-open", str(self.download.downloadDirectory())]);


class DownloadPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Downloads", parent);
        self.setAllowedAreas(Qt.BottomDockWidgetArea);
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable);
        self._items: list[DownloadItemWidget] = [];
        self._build_ui();

    def _build_ui(self):
        container = QWidget();
        outer = QVBoxLayout(container);
        outer.setContentsMargins(0, 0, 0, 0);

        header_row = QHBoxLayout();
        header_row.addStretch();
        btn_clear = QPushButton("Limpar concluídos");
        btn_clear.clicked.connect(self._clear_done);
        header_row.addWidget(btn_clear);
        outer.addLayout(header_row);

        scroll = QScrollArea();
        scroll.setWidgetResizable(True);
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
        self._list_widget = QWidget();
        self._list_layout = QVBoxLayout(self._list_widget);
        self._list_layout.setContentsMargins(4, 4, 4, 4);
        self._list_layout.setSpacing(4);
        self._list_layout.addStretch();
        scroll.setWidget(self._list_widget);
        outer.addWidget(scroll);

        self.setWidget(container);
        self.setMinimumHeight(160);

    def add_download(self, download: QWebEngineDownloadRequest):
        item = DownloadItemWidget(download);
        self._items.append(item);
        self._list_layout.insertWidget(self._list_layout.count() - 1, item);

    def _clear_done(self):
        done_states = {
            QWebEngineDownloadRequest.DownloadState.DownloadCompleted,
            QWebEngineDownloadRequest.DownloadState.DownloadCancelled,
            QWebEngineDownloadRequest.DownloadState.DownloadInterrupted,
        };
        for item in list(self._items):
            if item.download.state() in done_states:
                self._items.remove(item);
                item.setParent(None);
                item.deleteLater();


# ---------------------------------------------------------------------------
# Captura de cliques via QWebChannel
# ---------------------------------------------------------------------------

_CLICK_LISTENER_JS = """
(function() {
    if (typeof QWebChannel === 'undefined') return;
    new QWebChannel(qt.webChannelTransport, function(channel) {
        document.addEventListener('click', function(e) {
            var el = e.target;
            if (!el || !el.tagName) return;
            var tag  = el.tagName.toLowerCase();
            var id   = el.id || '';
            var name = el.getAttribute ? (el.getAttribute('name') || '') : '';
            channel.objects.capture.elementClicked(tag, id, name);
        }, true);
    });
})();
""";


class ClickCapture(QObject):
    def __init__(self, parent=None):
        super().__init__(parent);

    @Slot(str, str, str)
    def elementClicked(self, tag: str, id_: str, name: str):
        parts = [f"tag=<{tag}>"];
        if id_:
            parts.append(f"id=\"{id_}\"");
        if name:
            parts.append(f"name=\"{name}\"");
        print(f"[clique] {',  '.join(parts)}");


# ---------------------------------------------------------------------------
# Aba do navegador
# ---------------------------------------------------------------------------

class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent);

    def createWindow(self, window_type):
        p = self.parent();
        while p and not isinstance(p, MainWindow):
            p = p.parent();
        return p.add_tab() if p else None;


# ---------------------------------------------------------------------------
# Janela principal
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();
        self.setWindowTitle("WebCráudio");
        self.setMinimumSize(1024, 700);
        self.bookmarks = BookmarkManager();
        self.history = HistoryManager();
        DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True);
        self._build_ui();
        self._build_shortcuts();
        self._connect_downloads();
        self.add_tab(QUrl("https://duckduckgo.com"));

    def _connect_downloads(self):
        profile = QWebEngineProfile.defaultProfile();
        profile.setDownloadPath(str(DOWNLOADS_DIR));
        profile.downloadRequested.connect(self._on_download_requested);
        # injeta qwebchannel.js em todas as páginas antes do DOM ser construído
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
        # --- toolbar de navegação ---
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
        url_container = QWidget();
        url_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred);
        url_container_layout = QHBoxLayout(url_container);
        url_container_layout.setContentsMargins(0, 0, 0, 0);
        url_container_layout.setStretch(0, 1);
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding);
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

        # --- barra de favoritos ---
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

        # --- barra de progresso + abas ---
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

        # --- painel de downloads (dock inferior, oculto inicialmente) ---
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
        view = BrowserTab(self.tabs);
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
        view.page().runJavaScript(_CLICK_LISTENER_JS);
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
                self.setWindowTitle(f"{title} — WebCráudio");

    def _update_nav_buttons(self, view: BrowserTab):
        history = view.history();
        self.btn_back.setEnabled(history.canGoBack());
        self.btn_forward.setEnabled(history.canGoForward());


def main():
    app = QApplication(sys.argv);
    app.setApplicationName("WebCráudio");
    window = MainWindow();
    window.show();
    sys.exit(app.exec());


if __name__ == "__main__":
    main();
