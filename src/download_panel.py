import os;
import sys;
import subprocess;
from pathlib import Path;
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QFrame, QLabel,
    QProgressBar, QSizePolicy,
);
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest;
from PySide6.QtCore import Qt, QTimer;


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
