from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QDialogButtonBox, QInputDialog,
);
from PySide6.QtCore import Qt;
from .bookmark_manager import BookmarkManager;


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
