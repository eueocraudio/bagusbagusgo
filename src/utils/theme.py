DARK_STYLESHEET = """
/* ── Base ─────────────────────────────────────────────────────────── */
QWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
    border: none;
    outline: none;
}

QMainWindow {
    background-color: #111111;
}

/* ── Outer + Inner TabWidget ──────────────────────────────────────── */
QTabWidget::pane {
    background-color: #1a1a1a;
    border-top: 2px solid #c0392b;
}

QTabBar {
    background-color: #111111;
}

QTabBar::tab {
    background-color: #1e1e1e;
    color: #999999;
    padding: 6px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:selected {
    background-color: #2a2a2a;
    color: #ffffff;
    border-bottom: 2px solid #c0392b;
}

QTabBar::tab:hover:!selected {
    background-color: #252525;
    color: #cccccc;
    border-bottom: 2px solid #7b241c;
}

QTabBar::tab:selected:top {
    border-top: 2px solid #c0392b;
    border-left: 1px solid #3a3a3a;
    border-right: 1px solid #3a3a3a;
    border-bottom: none;
}

QTabBar::close-button {
    subcontrol-position: right;
}

/* ── Botões ───────────────────────────────────────────────────────── */
QPushButton {
    background-color: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 3px 8px;
}

QPushButton:hover {
    background-color: #3a3a3a;
    border: 1px solid #c0392b;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #7b241c;
    border: 1px solid #c0392b;
}

QPushButton:disabled {
    background-color: #1e1e1e;
    color: #555555;
    border: 1px solid #2a2a2a;
}

QToolButton {
    background-color: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 3px;
}

QToolButton:hover {
    background-color: #3a3a3a;
    border: 1px solid #c0392b;
    color: #ffffff;
}

QToolButton:pressed, QToolButton::menu-indicator {
    background-color: #7b241c;
}

QToolButton::menu-indicator {
    image: none;
    width: 0px;
}

/* ── Barra de endereço ────────────────────────────────────────────── */
QLineEdit {
    background-color: #242424;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 3px 8px;
    selection-background-color: #c0392b;
}

QLineEdit:focus {
    border: 1px solid #c0392b;
    background-color: #1e1e1e;
}

/* ── Progress bar ─────────────────────────────────────────────────── */
QProgressBar {
    background-color: #111111;
    border: none;
}

QProgressBar::chunk {
    background-color: #c0392b;
}

/* ── Barra de status ──────────────────────────────────────────────── */
QStatusBar {
    background-color: #111111;
    color: #888888;
    border-top: 1px solid #c0392b;
}

/* ── Menu ─────────────────────────────────────────────────────────── */
QMenu {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #c0392b;
    padding: 4px 0px;
}

QMenu::item {
    padding: 6px 24px;
}

QMenu::item:selected {
    background-color: #c0392b;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #c0392b;
    margin: 3px 8px;
}

/* ── Listas ───────────────────────────────────────────────────────── */
QListWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    alternate-background-color: #242424;
}

QListWidget::item:selected {
    background-color: #7b241c;
    color: #ffffff;
    border-left: 3px solid #c0392b;
}

QListWidget::item:hover:!selected {
    background-color: #2a2a2a;
    border-left: 3px solid #555555;
}

/* ── Scroll ───────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background-color: #1a1a1a;
    width: 8px;
    border-left: 1px solid #2a2a2a;
}

QScrollBar::handle:vertical {
    background-color: #3a3a3a;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #c0392b;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1a1a1a;
    height: 8px;
    border-top: 1px solid #2a2a2a;
}

QScrollBar::handle:horizontal {
    background-color: #3a3a3a;
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #c0392b;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ── Diálogos ─────────────────────────────────────────────────────── */
QDialog {
    background-color: #1a1a1a;
    border: 1px solid #c0392b;
}

QMessageBox {
    background-color: #1a1a1a;
}

QDialogButtonBox QPushButton {
    min-width: 72px;
}

/* ── Dock ─────────────────────────────────────────────────────────── */
QDockWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
    titlebar-close-icon: none;
}

QDockWidget::title {
    background-color: #111111;
    padding: 4px 8px;
    border-bottom: 2px solid #c0392b;
    text-align: left;
}

/* ── Frame (DownloadItemWidget) ───────────────────────────────────── */
QFrame[frameShape="4"] {
    border: 1px solid #3a3a3a;
    border-left: 3px solid #c0392b;
    border-radius: 4px;
    background-color: #1e1e1e;
}

/* ── Labels ───────────────────────────────────────────────────────── */
QLabel {
    color: #e0e0e0;
    background-color: transparent;
}

/* ── Input dialog ─────────────────────────────────────────────────── */
QInputDialog QLineEdit {
    border: 1px solid #c0392b;
}

/* ── Separadores ──────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #c0392b;
}
""";
