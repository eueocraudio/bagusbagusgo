# BagusBagusGo (BBGo) — instruções para o Claude

## Versão atual

**v2.0.0** — constantes em `src/constants.py` (`APP_NAME`, `APP_VERSION`, `APP_ID`).

## Visão geral

Browser desktop construído com Python 3 e PySide6 (QtWebEngine).  
Entry point: `run.py`. Toda a lógica de UI está em `src/main_window.py`.

## Como rodar

```bash
# Diretório temporário gerado em /tmp/
python3 run.py

# Diretório específico
python3 run.py /caminho/do/diretorio
```

`sys.argv` é passado explicitamente: `run.py` → `main(sys.argv)` → `QApplication(args)`.

## Estrutura de arquivos

```
run.py                      — entry point; passa sys.argv para main()
data/
  user_agents.txt           — lista de user agents (um por linha)
src/
  browser.py                — main(args): lê args, aplica tema, inicia MainWindow
  constants.py              — APP_NAME, APP_VERSION, APP_ID, HISTORY_MAX, DEFAULT_DATA_DIR
  theme.py                  — DARK_STYLESHEET (dark + vermelho)
  user_agent.py             — random_user_agent(), navigator_spoof_script(ua)
  request_interceptor.py    — UserAgentInterceptor, YOUTUBE_UA, YOUTUBE_SPOOF_JS
  session_manager.py        — SessionManager: salva/restaura URLs das abas
  bookmark_manager.py       — BookmarkManager (CRUD JSON)
  bookmarks_dialog.py       — ManageBookmarksDialog
  history_manager.py        — HistoryManager (registro e busca, máx. 5000)
  history_dialog.py         — HistoryDialog
  download_panel.py         — DownloadItemWidget + DownloadPanel
  click_capture.py          — ClickCapture + CLICK_LISTENER_JS
  browser_tab.py            — BrowserTab (recebe add_tab como callback)
  main_window.py            — MainWindow (orquestra tudo)
  myass/
    __init__.py
    panel.py                — MyAssPanel (barra de botões + tabela 4 colunas)
install.sh                  — instala dependências via pip3
```

## Dados gerados em runtime

Todos os arquivos ficam no diretório passado como argumento (ou `/tmp/bagusbagusgo_<id>/`):

| Arquivo | Conteúdo |
|---|---|
| `<base_dir>/bookmarks.json` | Favoritos |
| `<base_dir>/history.json`   | Histórico de navegação |
| `<base_dir>/session.json`   | URLs das abas para restauração |
| `<base_dir>/downloads/`     | Arquivos baixados |

## Arquitetura — classes principais

| Classe / módulo | Responsabilidade |
|---|---|
| `BookmarkManager` | CRUD de favoritos em JSON |
| `ManageBookmarksDialog` | Diálogo para renomear/remover favoritos |
| `HistoryManager` | Registro e busca de histórico |
| `HistoryDialog` | Diálogo com busca, agrupamento por data e limpeza |
| `SessionManager` | Salva URLs no `closeEvent`; restaura na inicialização |
| `ClickCapture` | `QObject` com `@Slot` — recebe cliques via `QWebChannel` → `print()` |
| `DownloadItemWidget` | Widget de progresso por arquivo baixado |
| `DownloadPanel` | `QDockWidget` inferior com lista de downloads |
| `BrowserTab` | `QWebEngineView`; recebe `add_tab` como callback |
| `MainWindow` | Janela principal — orquestra tudo |
| `MyAssPanel` | Painel da aba MyAss: barra de botões (New work, New flow) + tabela Work/Flow/Status/Date |
| `DARK_STYLESHEET` | Stylesheet global dark + vermelho aplicado no `QApplication` |
| `random_user_agent()` | Lê `data/user_agents.txt` e retorna UA aleatório |
| `navigator_spoof_script(ua)` | Gera JS que sobrescreve `navigator.*` para mascarar QtWebEngine |
| `UserAgentInterceptor` | Substitui header `User-Agent` nas requisições HTTP por domínio |

## Layout da janela

```
MainWindow  (título: "BagusBagusGo v2.0.0")
└── outer QTabWidget (5 abas)
    ├── [1] BagusBagusGo  ← browser completo
    │    ├── nav_bar (QWidget + QHBoxLayout)
    │    │    └── ← → ↻ ⌂  [URL bar]  ☆ ★≡ 🕐 ⬇ + ⚙
    │    ├── bookmarks_bar (QWidget, visível só com favoritos)
    │    ├── progress_bar
    │    └── QTabWidget interno (abas das páginas web)
    ├── [2] MyAss       ← MyAssPanel
    ├── [3] Anonymity
    ├── [4] AutoBot
    └── [5] Downloads
```

## Configurações do QWebEngineProfile

Aplicadas em `MainWindow._connect_downloads()`:

| Configuração | Valor |
|---|---|
| `ForceDarkMode` | `True` |
| `HttpUserAgent` | Aleatório a cada inicialização |
| `DownloadPath` | `<base_dir>/downloads/` |
| `navigator_spoof` script | Injeta em `DocumentCreation` — sobrescreve `navigator.*` |
| `youtube_ua_spoof` script | Injeta em `DocumentCreation` — spoof completo para youtube.com |
| `youtube_ad_skipper` script | Injeta em `DocumentReady` — pula propagandas automaticamente |
| `qwebchannel.js` | Injeta em `DocumentCreation` via `QWebEngineScript` |
| `UserAgentInterceptor` | youtube.com → `Firefox/140.0` no header HTTP |

## Comportamentos automáticos por URL

| Condição (`_on_load_finished`) | Ação |
|---|---|
| `"google.com" in url` | Redireciona para `https://duckduckgo.com` |
| YouTube (via script) | Pula propagandas a cada 500ms |

## Sessão

- `closeEvent` salva URLs de todas as abas em `session.json`
- Na inicialização, `_restore_session()` reabre as abas salvas
- Se não houver sessão, abre `https://duckduckgo.com`

## Fechar aba

`close_tab()` pausa e limpa `src` de todos os `<video>` e `<audio>` antes de remover a aba.

## Injeção de JavaScript por URL

```python
if "site.com" in url:
    view.page().runJavaScript("/* JS aqui */");
```

## Regras de desenvolvimento

- Todo código novo vai em `src/`
- Usar PySide6 para qualquer elemento de interface
- Terminar instruções Python com `;`
- Usar 4 espaços para indentação (nunca TAB)
- Não usar `QApplication.exec_()` — usar `app.exec()`
- Motor de busca: DuckDuckGo (`https://duckduckgo.com/?q=`)
- `BrowserTab` recebe `add_tab` como callback — não importa `MainWindow`
- Barras de navegação/favoritos são `QWidget` + `QHBoxLayout`, não `QToolBar`
- Versão centralizada em `src/constants.py` — nunca hardcodar em outro lugar
- User agents em `data/user_agents.txt` — um por linha
- Tema em `src/theme.py` — editar `DARK_STYLESHEET` para mudar cores
