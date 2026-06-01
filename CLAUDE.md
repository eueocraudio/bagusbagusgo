# BagusBagusGo — instruções para o Claude

## Visão geral

Browser desktop construído com Python 3 e PySide6 (QtWebEngine).  
Toda a interface está em `src/main_window.py`. Entry point: `run.py`.

## Como rodar

```bash
# Diretório gerado automaticamente em /tmp/
python3 run.py

# Diretório específico
python3 run.py /caminho/do/diretorio
```

## Estrutura de arquivos

```
run.py                    — entry point
data/
  user_agents.txt         — lista de user agents (um por linha)
src/
  browser.py              — main(): lê argv, aplica tema, inicia MainWindow
  constants.py            — HISTORY_MAX, DEFAULT_DATA_DIR
  theme.py                — DARK_STYLESHEET (dark + vermelho)
  user_agent.py           — random_user_agent(): lê data/user_agents.txt
  bookmark_manager.py     — BookmarkManager (CRUD JSON)
  bookmarks_dialog.py     — ManageBookmarksDialog
  history_manager.py      — HistoryManager (registro e busca, máx. 5000)
  history_dialog.py       — HistoryDialog
  download_panel.py       — DownloadItemWidget + DownloadPanel
  click_capture.py        — ClickCapture + CLICK_LISTENER_JS
  browser_tab.py          — BrowserTab (recebe add_tab como callback)
  main_window.py          — MainWindow (orquestra tudo)
  myass/
    __init__.py
    panel.py              — MyAssPanel (barra de botões + tabela)
install.sh                — instala dependências via pip3
```

## Dados gerados em runtime

Todos os arquivos gerados ficam no diretório passado como argumento (ou em `/tmp/bagusbagusgo_<id>/` se nenhum for informado):

| Arquivo | Conteúdo |
|---|---|
| `<base_dir>/bookmarks.json` | Favoritos |
| `<base_dir>/history.json`   | Histórico de navegação |
| `<base_dir>/downloads/`     | Arquivos baixados |

## Arquitetura — classes principais

| Classe / módulo | Responsabilidade |
|---|---|
| `BookmarkManager` | CRUD de favoritos em JSON |
| `ManageBookmarksDialog` | Diálogo para renomear/remover favoritos |
| `HistoryManager` | Registro e busca de histórico |
| `HistoryDialog` | Diálogo com busca, agrupamento por data e limpeza |
| `ClickCapture` | `QObject` com `@Slot` — recebe cliques via `QWebChannel` → `print()` |
| `DownloadItemWidget` | Widget de progresso por arquivo baixado |
| `DownloadPanel` | `QDockWidget` inferior com lista de downloads |
| `BrowserTab` | `QWebEngineView`; recebe `add_tab` como callback |
| `MainWindow` | Janela principal — orquestra tudo |
| `DARK_STYLESHEET` | Stylesheet global dark + vermelho aplicado no `QApplication` |
| `random_user_agent()` | Lê `data/user_agents.txt` e retorna UA aleatório |
| `MyAssPanel` | Painel da aba MyAss: barra de botões (direita) + tabela 4 colunas |

## Layout da janela

```
MainWindow
└── outer QTabWidget (5 abas)
    ├── [1] BagusBagusGo  ← browser completo
    │    ├── nav_bar (QWidget + QHBoxLayout)
    │    │    └── ← → ↻ ⌂  [URL bar]  ☆ ★≡ 🕐 ⬇ + ⚙
    │    ├── bookmarks_bar (QWidget, visível só com favoritos)
    │    ├── progress_bar
    │    └── QTabWidget interno (abas das páginas web)
    ├── [2] MyAss
    ├── [3] Anonymity
    ├── [4] AutoBot
    └── [5] Downloads
```

## Configurações do QWebEngineProfile

Aplicadas em `MainWindow._connect_downloads()`:

| Configuração | Valor |
|---|---|
| `ForceDarkMode` | `True` — força dark mode nas páginas web |
| `HttpUserAgent` | Aleatório a cada inicialização (lido de `data/user_agents.txt`) |
| `DownloadPath` | `<base_dir>/downloads/` |
| `qwebchannel.js` | Injetado em toda página via `QWebEngineScript` (DocumentCreation) |

## Injeção de JavaScript por URL

Ponto de extensão: `_on_load_finished` em `MainWindow`.

```python
if "site.com" in url:
    view.page().runJavaScript("/* JS aqui */");
```

**Regras ativas:**

| Condição | Ação |
|---|---|
| `"google.com" in url` | Redireciona para `https://duckduckgo.com` |

## Captura de cliques

`CLICK_LISTENER_JS` é injetado após cada `loadFinished`. Envia `tag`, `id` e `name` do elemento clicado via `QWebChannel` → `ClickCapture.elementClicked` → `print()`.

## Regras de desenvolvimento

- Todo código novo vai em `src/`
- Usar PySide6 para qualquer elemento de interface
- Terminar instruções Python com `;`
- Usar 4 espaços para indentação (nunca TAB)
- Não usar `QApplication.exec_()` (deprecated) — usar `app.exec()`
- Motor de busca padrão: DuckDuckGo (`https://duckduckgo.com/?q=`)
- Página inicial e botão home: `https://duckduckgo.com`
- `BrowserTab` recebe `add_tab` como callback — não importa `MainWindow`
- Barras de navegação e favoritos são `QWidget` + `QHBoxLayout`, não `QToolBar`
- Ao adicionar nova aba externa: `self.outer_tabs.addTab(QWidget(), "Nome")`
- User agents ficam em `data/user_agents.txt` — um por linha, linhas vazias ignoradas
- Tema visual em `src/theme.py` — editar `DARK_STYLESHEET` para mudar cores
