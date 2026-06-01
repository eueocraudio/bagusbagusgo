from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
);
from PySide6.QtCore import Qt;


class MyAssPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        layout = QVBoxLayout(self);
        layout.setContentsMargins(8, 8, 8, 8);
        layout.setSpacing(6);
        layout.addLayout(self._build_toolbar());
        layout.addWidget(self._build_table());

    def _build_toolbar(self) -> QHBoxLayout:
        bar = QHBoxLayout();
        bar.addStretch();
        btn_new_work = QPushButton("New work");
        btn_new_work.setFixedHeight(30);
        bar.addWidget(btn_new_work);
        btn_new_flow = QPushButton("New flow");
        btn_new_flow.setFixedHeight(30);
        bar.addWidget(btn_new_flow);
        return bar;

    def _build_table(self) -> QTableWidget:
        self.table = QTableWidget(0, 4);
        self.table.setHorizontalHeaderLabels(["Work", "Flow", "Status", "Date"]);
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);
        self.table.verticalHeader().setVisible(False);
        self.table.setEditTriggers(QTableWidget.NoEditTriggers);
        self.table.setSelectionBehavior(QTableWidget.SelectRows);
        self.table.setAlternatingRowColors(True);
        return self.table;
