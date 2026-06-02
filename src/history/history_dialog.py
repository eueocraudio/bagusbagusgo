from datetime import datetime, date, timedelta;
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton,
    QDialogButtonBox, QMessageBox,
);
from PySide6.QtCore import Qt, Signal;
from .history_manager import HistoryManager;


class HistoryDialog(QDialog):
    url_requested = Signal(str);

    def __init__(self, manager: HistoryManager, parent=None):
        super().__init__(parent);
        self._manager = manager;
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
        entries = self._manager.search(query) if query else self._manager.all();
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
            item.setData(Qt.UserRole, (entry["visited_at"], entry["url"]));
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
        visited_at, _ = item.data(Qt.UserRole);
        self._manager.remove(visited_at);
        self._populate(self.search_bar.text());

    def _clear_all(self):
        resp = QMessageBox.question(
            self, "Limpar histórico",
            "Apagar todo o histórico de navegação?",
            QMessageBox.Yes | QMessageBox.No,
        );
        if resp == QMessageBox.Yes:
            self._manager.clear();
            self._populate(self.search_bar.text());
