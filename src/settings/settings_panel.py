import threading;
from pathlib import Path;
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QPlainTextEdit,
    QTabWidget, QGroupBox, QMessageBox, QFrame,
    QGridLayout, QScrollArea,
);
from PySide6.QtCore import Qt, Signal, QObject, QEvent;
from ..privacy.ua_updater import update as ua_update, _UA_FILE;
from ..privacy.ads_updater import update as ads_update;
from ..privacy.ad_blocker import PERSONAL_FILE as _ADS_FILE, WEB_FILE as _ADS_WEB_FILE;
from . import websettings_manager as _wsm;

_ROOT = Path(__file__).parent.parent.parent;

class _Worker(QObject):
    done = Signal(int, str);


_ENV_VARS = [
    ("UBLOCK_ENABLED",              "uBlock Origin",                     True),
    ("AD_BLOCKER_ENABLED",          "Bloqueador CSS de anúncios",        False),
    ("AD_SELECTOR_PERSONAL_ENABLED","Ad Selectors — lista pessoal",      True),
    ("AD_SELECTOR_WEB_ENABLED",     "Ad Selectors — lista da internet",  False),
    ("WEBGL_FORCE",                 "Forçar WebGL/GPU",                  False),
];


class _FileEditor(QWidget):
    def __init__(self, path: Path, filter_comments: bool = False, show_update_btn: bool = False, readonly: bool = False, autosave: bool = False, _update_fn=None, parent=None):
        super().__init__(parent);
        self._path = path;
        self._filter_comments = filter_comments;
        self._update_fn = _update_fn or ua_update;
        layout = QVBoxLayout(self);
        layout.setContentsMargins(8, 8, 8, 8);

        if show_update_btn:
            self._worker = _Worker();
            self._worker.done.connect(self._on_update_done);
            top_bar = QHBoxLayout();
            self._btn_update = QPushButton("Update");
            self._btn_update.setFixedWidth(90);
            self._btn_update.clicked.connect(self._on_update);
            top_bar.addWidget(self._btn_update);
            top_bar.addStretch();
            layout.addLayout(top_bar);

        self._autosave = autosave;
        self._editor = QPlainTextEdit();
        self._editor.setLineWrapMode(QPlainTextEdit.NoWrap);
        self._editor.setReadOnly(readonly);
        if autosave:
            self._editor.installEventFilter(self);
        layout.addWidget(self._editor);

        if not readonly and not autosave:
            btn_bar = QHBoxLayout();
            btn_bar.addStretch();
            self._btn_save = QPushButton("Salvar");
            self._btn_save.setFixedWidth(90);
            self._btn_save.clicked.connect(self._save);
            btn_bar.addWidget(self._btn_save);
            layout.addLayout(btn_bar);

        self._reload();

    def _reload(self):
        if not self._path.exists():
            self._editor.setPlainText("");
            return;
        lines = self._path.read_text(encoding="utf-8").splitlines();
        if self._filter_comments:
            lines = [l for l in lines if l.strip() and not l.strip().startswith("#")];
        self._editor.setPlainText("\n".join(lines));

    def _on_update(self):
        self._btn_update.setEnabled(False);
        self._btn_update.setText("...");
        def _run():
            count, msg = self._update_fn(self._path);
            self._worker.done.emit(count, msg);
        threading.Thread(target=_run, daemon=True).start();

    def _on_update_done(self, count: int, msg: str):
        self._btn_update.setEnabled(True);
        self._btn_update.setText("Update");
        if count:
            self._reload();
        QMessageBox.information(self, "Update", msg);

    def eventFilter(self, obj, event):
        if obj is self._editor and event.type() == QEvent.Type.FocusOut:
            self._save();
        return super().eventFilter(obj, event);

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True);
        self._path.write_text(self._editor.toPlainText(), encoding="utf-8");
        if not self._autosave:
            QMessageBox.information(self, "Salvo", f"Arquivo salvo:\n{self._path}");


class _EnvEditor(QWidget):
    def __init__(self, env_file: Path, parent=None):
        super().__init__(parent);
        self._env_file = env_file;
        layout = QVBoxLayout(self);
        layout.setContentsMargins(16, 16, 16, 16);
        layout.setSpacing(12);

        box = QGroupBox("Options");
        box_layout = QVBoxLayout(box);
        box_layout.setSpacing(10);

        note = QLabel(f"Editando: {env_file}\nAs alterações têm efeito na próxima inicialização do app.");
        note.setWordWrap(True);
        note.setStyleSheet("color: #888; font-size: 11px;");
        box_layout.addWidget(note);

        self._checks: dict[str, QCheckBox] = {};
        import os as _os;
        for key, label, default in _ENV_VARS:
            cb = QCheckBox(label);
            val = _os.environ.get(key, str(default)).strip().lower();
            cb.setChecked(val in ("true", "1", "yes"));
            cb.setToolTip(f"{key}");
            cb.stateChanged.connect(self._save);
            self._checks[key] = cb;
            box_layout.addWidget(cb);

        layout.addWidget(box);

        line = QFrame();
        line.setFrameShape(QFrame.HLine);
        line.setFrameShadow(QFrame.Plain);
        line.setStyleSheet("background-color: #cc0000; max-height: 2px; border: none;");
        layout.addWidget(line);
        layout.addStretch();

    def _load_env(self) -> dict:
        result = {};
        if not self._env_file.exists():
            return result;
        for line in self._env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip();
            if not line or line.startswith("#") or "=" not in line:
                continue;
            k, _, v = line.partition("=");
            result[k.strip()] = v.strip();
        return result;

    def _save(self):
        current = self._load_env();
        for key, cb in self._checks.items():
            current[key] = "true" if cb.isChecked() else "false";
        lines = [];
        seen: set[str] = set();
        if self._env_file.exists():
            for line in self._env_file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip();
                if stripped.startswith("#") or "=" not in stripped:
                    lines.append(line);
                    continue;
                k, _, _ = stripped.partition("=");
                k = k.strip();
                if k in seen:
                    continue;
                seen.add(k);
                if k in current:
                    lines.append(f"{k}={current.pop(k)}");
                else:
                    lines.append(line);
        for k, v in current.items():
            lines.append(f"{k}={v}");
        self._env_file.parent.mkdir(parents=True, exist_ok=True);
        self._env_file.write_text("\n".join(lines) + "\n", encoding="utf-8");


class _AdsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent);
        layout = QVBoxLayout(self);
        layout.setContentsMargins(8, 8, 8, 8);
        layout.setSpacing(8);

        grp_personal = QGroupBox("Lista Pessoal");
        grp_layout = QVBoxLayout(grp_personal);
        self._personal_editor = _FileEditor(_ADS_FILE, filter_comments=True, autosave=True);
        grp_layout.addWidget(self._personal_editor);
        layout.addWidget(grp_personal, stretch=1);

        line = QFrame();
        line.setFrameShape(QFrame.HLine);
        line.setFrameShadow(QFrame.Plain);
        line.setStyleSheet("background-color: #cc0000; max-height: 2px; border: none;");
        layout.addWidget(line);

        grp_web = QGroupBox("Lista da Internet");
        grp_web_layout = QVBoxLayout(grp_web);
        self._web_editor = _FileEditor(
            _ADS_WEB_FILE,
            filter_comments=True,
            show_update_btn=True,
            readonly=True,
            _update_fn=ads_update,
        );
        grp_web_layout.addWidget(self._web_editor);
        layout.addWidget(grp_web, stretch=1);


_WS_DESCRIPTIONS: dict[str, str] = {
    "Accelerated2dCanvasEnabled":         "Usa GPU para renderizar canvas 2D",
    "AllowGeolocationOnInsecureOrigins":  "Permite geolocalização em páginas sem HTTPS",
    "AllowRunningInsecureContent":        "Permite conteúdo HTTP em páginas HTTPS",
    "AllowWindowActivationFromJavaScript":"Permite JS trazer janela para frente",
    "AutoLoadIconsForPage":               "Carrega favicons das páginas automaticamente",
    "AutoLoadImages":                     "Carrega imagens automaticamente",
    "BackForwardCacheEnabled":            "Cache de páginas para navegação rápida ←→",
    "DnsPrefetchEnabled":                 "Pré-resolve DNS de links antes de clicar",
    "ErrorPageEnabled":                   "Exibe página de erro quando falha ao carregar",
    "FocusOnNavigationEnabled":           "Foca a janela ao navegar para uma URL",
    "ForceDarkMode":                      "Força modo escuro em todas as páginas",
    "FullScreenSupportEnabled":           "Permite páginas entrarem em tela cheia",
    "HyperlinkAuditingEnabled":           "Envia ping de rastreamento em links (<a ping>)",
    "JavascriptCanAccessClipboard":       "Permite JS ler/escrever na área de transferência",
    "JavascriptCanOpenWindows":           "Permite JS abrir novas janelas/popups",
    "JavascriptCanPaste":                 "Permite JS colar texto da área de transferência",
    "JavascriptEnabled":                  "Habilita execução de JavaScript",
    "LinksIncludedInFocusChain":          "Inclui links na navegação por Tab",
    "LocalContentCanAccessFileUrls":      "Páginas locais podem acessar outros arquivos locais",
    "LocalContentCanAccessRemoteUrls":    "Páginas locais podem acessar URLs remotas",
    "LocalStorageEnabled":                "Habilita localStorage e sessionStorage",
    "NavigateOnDropEnabled":              "Navega para URL ao soltar arquivo/texto na janela",
    "PdfViewerEnabled":                   "Abre PDFs direto no browser",
    "PlaybackRequiresUserGesture":        "Exige interação do usuário para reproduzir mídia",
    "PluginsEnabled":                     "Habilita plugins externos (ex: Flash)",
    "PreferCSSMarginsForPrinting":        "Usa margens CSS ao imprimir",
    "PrintElementBackgrounds":            "Imprime cores/imagens de fundo dos elementos",
    "PrintHeaderAndFooter":               "Imprime cabeçalho e rodapé padrão",
    "ReadingFromCanvasEnabled":           "Permite JS ler pixels do canvas (getImageData)",
    "ScreenCaptureEnabled":               "Permite páginas capturar a tela",
    "ScrollAnimatorEnabled":              "Anima rolagem suavemente",
    "ShowScrollBars":                     "Exibe barras de rolagem",
    "SpatialNavigationEnabled":           "Navegação espacial com setas do teclado",
    "TouchEventsApiEnabled":              "Habilita API de eventos de toque",
    "TouchIconsEnabled":                  "Carrega ícones touch (apple-touch-icon)",
    "TrimAccessibilityIdentifiers":       "Remove identificadores de acessibilidade longos",
    "WebGLEnabled":                       "Habilita WebGL para gráficos 3D",
    "WebRTCPublicInterfacesOnly":         "WebRTC usa apenas IPs públicos (privacidade)",
    "XSSAuditingEnabled":                 "Filtro de XSS no Chromium (obsoleto)",
};

_CB_STYLE = """
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 2px solid #6b0000;
    border-radius: 3px;
    background-color: #1a0000;
}
QCheckBox::indicator:checked {
    background-color: #8b0000;
    border: 2px solid #cc0000;
    image: none;
}
QCheckBox::indicator:hover {
    border: 2px solid #cc0000;
}
""";


class _WebSettingsPanel(QWidget):
    def __init__(self, base_dir: Path, profile, parent=None):
        super().__init__(parent);
        self._base_dir = base_dir;
        self._profile  = profile;
        self._settings = _wsm.load(base_dir);
        self._checks: dict[str, QCheckBox] = {};

        scroll = QScrollArea();
        scroll.setWidgetResizable(True);
        scroll.setFrameShape(QFrame.NoFrame);

        container = QWidget();
        grid = QGridLayout(container);
        grid.setContentsMargins(12, 12, 12, 12);
        grid.setHorizontalSpacing(32);
        grid.setVerticalSpacing(6);

        names = sorted(self._settings.keys());
        cols = 3;
        for i, name in enumerate(names):
            desc = _WS_DESCRIPTIONS.get(name, "");
            cb = QCheckBox(name);
            cb.setChecked(self._settings[name]);
            cb.setToolTip(desc);
            cb.setStyleSheet(_CB_STYLE);
            if desc:
                lbl = QLabel(desc);
                lbl.setStyleSheet("color: #ff8c00; font-size: 10px; padding-left: 22px;");
                lbl.setWordWrap(True);
                cell = QWidget();
                cell_layout = QVBoxLayout(cell);
                cell_layout.setContentsMargins(0, 0, 0, 4);
                cell_layout.setSpacing(1);
                cell_layout.addWidget(cb);
                cell_layout.addWidget(lbl);
                grid.addWidget(cell, i // cols, i % cols);
            else:
                grid.addWidget(cb, i // cols, i % cols);
            cb.stateChanged.connect(lambda state, k=name: self._on_change(k, bool(state)));
            self._checks[name] = cb;

        scroll.setWidget(container);

        layout = QVBoxLayout(self);
        layout.setContentsMargins(0, 0, 0, 0);
        layout.addWidget(scroll);

    def _on_change(self, key: str, value: bool):
        self._settings[key] = value;
        _wsm.save(self._base_dir, self._settings);
        _wsm.apply(self._profile, {key: value});


class SettingsPanel(QWidget):
    def __init__(self, base_dir: Path = None, profile=None, parent=None):
        super().__init__(parent);
        env_file = Path(base_dir) / ".env" if base_dir else _ROOT / ".env";
        layout = QVBoxLayout(self);
        layout.setContentsMargins(0, 0, 0, 0);

        tabs = QTabWidget();
        tabs.addTab(_EnvEditor(env_file),                                                              "Geral");
        tabs.addTab(_WebSettingsPanel(base_dir, profile) if base_dir and profile else QWidget(),       "Browser");
        tabs.addTab(_FileEditor(_UA_FILE, filter_comments=True, show_update_btn=True, readonly=True),  "User Agents");
        tabs.addTab(_AdsPanel(),                                                                        "Ad Selectors");
        layout.addWidget(tabs);
