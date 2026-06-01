# BagusBagusGo — instruções para o Claude

## Visão geral

Browser desktop construído com Python 3 e PySide6 (QtWebEngine). Toda a lógica está em `src/browser.py`.

## Como rodar

```bash
python3 run.py
```

## Estrutura

```
run.py                    — entry point (executa src/browser.main)
src/
  browser.py              — main() e entry point do pacote
  constants.py            — constantes globais (paths, limites)
  bookmark_manager.py     — BookmarkManager (CRUD JSON)
  bookmarks_dialog.py     — ManageBookmarksDialog
  history_manager.py      — HistoryManager (registro e busca)
  history_dialog.py       — HistoryDialog
  download_panel.py       — DownloadItemWidget + DownloadPanel
  click_capture.py        — ClickCapture + CLICK_LISTENER_JS
  browser_tab.py          — BrowserTab (recebe add_tab como callback)
  main_window.py          — MainWindow (orquestra tudo)
install.sh                — instala dependências via pip3
```

## Dados persistidos pelo usuário

| Arquivo | Conteúdo |
|---|---|
| `~/.config/bagusbagusgo/bookmarks.json` | Favoritos |
| `~/.config/bagusbagusgo/history.json`   | Histórico de navegação |
| `~/Downloads/`                            | Arquivos baixados |

## Arquitetura de `src/browser.py`

| Classe | Responsabilidade |
|---|---|
| `BookmarkManager` | CRUD de favoritos em JSON |
| `ManageBookmarksDialog` | Diálogo para renomear/remover favoritos |
| `HistoryManager` | Registro e busca de histórico (máx. 5000 entradas) |
| `HistoryDialog` | Diálogo com busca, agrupamento por data e limpeza |
| `ClickCapture` | `QObject` com `@Slot` que recebe cliques do JS via `QWebChannel` e imprime tag/id/name no terminal |
| `DownloadItemWidget` | Widget de progresso por arquivo baixado |
| `DownloadPanel` | `QDockWidget` inferior com lista de downloads |
| `BrowserTab` | `QWebEngineView`; `createWindow` sobe o chain de parents até `MainWindow` para abrir links em nova aba |
| `MainWindow` | Janela principal: toolbars, abas, atalhos, orquestra tudo |

## Layout da janela

```
MainWindow
└── outer QTabWidget (5 abas)
    ├── [1] BagusBagusGo  ← browser completo
    │    ├── nav_bar (QWidget + QHBoxLayout)
    │    │    └── ← → ↻ ⌂ [URL bar] ☆ ★≡ 🕐 ⬇ + ⚙
    │    ├── bookmarks_bar (QWidget, visível só com favoritos)
    │    ├── progress_bar
    │    └── QTabWidget interno (abas das páginas web)
    ├── [2] MyAss
    ├── [3] Anonymity
    ├── [4] AutoBot
    └── [5] Downloads
```

As barras de navegação e favoritos são `QWidget` com `QHBoxLayout` (não `QToolBar`), permitindo que fiquem dentro de uma aba do `outer_tabs`.

## Injeção de JavaScript por URL

O ponto de extensão para automações é `_on_load_finished` em `MainWindow`. Após cada página carregar, verificar a URL e chamar `view.page().runJavaScript(...)`:

```python
def _on_load_finished(self, view: BrowserTab):
    url = view.url().toString();
    ...
    if "site.com" in url:
        view.page().runJavaScript("/* JS aqui */");
```

**Regras ativas no momento:**

| Condição | Ação |
|---|---|
| `"google.com" in url` | Redireciona para `https://duckduckgo.com` via `window.location.href` |

Ao adicionar nova regra, atualizar a tabela acima.

## Captura de cliques

`qwebchannel.js` é injetado em todas as páginas via `QWebEngineScript` no perfil (`DocumentCreation`, `MainWorld`). Após cada `loadFinished`, `_CLICK_LISTENER_JS` instala um `addEventListener('click')` que envia `tag`, `id` e `name` do elemento clicado ao Python via `QWebChannel` → `ClickCapture.elementClicked` → `print()`.

## Regras de desenvolvimento

- Todo código novo vai em `src/`
- Usar PySide6 para qualquer elemento de interface
- Terminar instruções Python com `;`
- Usar 4 espaços para indentação (nunca TAB)
- Não usar `QApplication.exec_()` (deprecated); usar `app.exec()`
- Motor de busca padrão: DuckDuckGo (`https://duckduckgo.com/?q=`)
- Página inicial e botão home: `https://duckduckgo.com`
- `BrowserTab` recebe `add_tab` como callback no construtor — não importa `MainWindow` (evita import circular)
- O comando de execução é `python3 run.py` (não `python3 src/browser.py`)
- Barras de navegação e favoritos são `QWidget` + `QHBoxLayout`, não `QToolBar`
- Ao adicionar nova aba no `outer_tabs`, usar `self.outer_tabs.addTab(QWidget(), "Nome")`
