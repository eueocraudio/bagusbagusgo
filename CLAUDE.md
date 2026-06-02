# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# BagusBagusGo (BBGo) — instruções para o Claude

## Versão atual

**v2.0.4** — constantes em `src/utils/constants.py` (`APP_NAME`, `APP_VERSION`, `APP_ID`).

## Visão geral

Browser desktop construído com Python 3 e PySide6 (QtWebEngine).  
Entry point: `run.py`. Toda a lógica de UI está em `src/main_window.py`.

## Como rodar

```bash
# Diretório temporário gerado em /tmp/
python3 run.py

# Diretório específico (dados persistem entre execuções)
python3 run.py /caminho/do/diretorio
```

`sys.argv` é passado explicitamente: `run.py` → `main(sys.argv)` → `QApplication(args)`.

Logs gerados em `<base_dir>/`. São **dois loggers segmentados por origem** (`src/utils/logger.py`):

- `bagusbagusgo.log` — logger `bbgo`: eventos do app. `stdout`/`stderr` são redirecionados para cá; também ecoa no terminal.
- `webengine.log` — logger `bbgo.web` (`propagate=False`, arquivo apenas): ruído de conteúdo web (console JS, CORS, etc.), capturado via `LoggingWebEnginePage.javaScriptConsoleMessage` em `src/core/browser_tab.py`. Acesse o logger com `logger.web_logger()`.

## Instalação

```bash
sudo bash install.sh
```

Instala PySide6, copia arquivos para `~/.local/bin/bagus/`, registra o `.desktop` e cria o comando `bagus`.

## Estrutura de arquivos

```
run.py                      — entry point; passa sys.argv para main()
bagus                       — launcher shell (usado após instalação)
data/
  user_agents.txt           — lista de user agents (um por linha)
  ad_selectors.txt          — seletores CSS para bloqueio de anúncios
  extensions/
    uBlock0.chromium/       — extensão uBlock Origin estática
src/
  browser.py                — main(args): lê args, aplica flags Chromium, inicia MainWindow
  constants.py              — APP_NAME, APP_VERSION, APP_ID, HISTORY_MAX, DEFAULT_DATA_DIR
  theme.py                  — DARK_STYLESHEET (dark + vermelho)
  env_config.py             — carrega .env; get_bool(key, default)
  logger.py                 — setup(base_dir): logger do app (bbgo) + logger web (bbgo.web); web_logger()
  user_agent.py             — random_user_agent(), navigator_spoof_script(ua)
  request_interceptor.py    — UserAgentInterceptor (interceptor HTTP por domínio)
  ad_blocker.py             — build_ad_block_js(): JS baseado em data/ad_selectors.txt
  extension_manager.py      — load_extensions(profile): carrega extensões de data/extensions/
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
install.sh                  — instala dependências e registra o app (requer sudo)
resources/
  bagus.desktop             — arquivo .desktop para o menu de aplicativos
  bagus.png                 — ícone do app
```

## Configuração via `.env`

O arquivo `.env` na raiz do projeto é carregado automaticamente por `src/env_config.py` antes de qualquer outra inicialização. Variáveis disponíveis:

Carregamento em 4 níveis (cada um sobrescreve o anterior): `.env` do projeto → `~/.env` → `~/.local/bin/bagus/.env` → `<base_dir>/.env`.

| Variável | Padrão | Efeito |
|---|---|---|
| `WEBGL_FORCE=true` | `false` | Força WebGL/GPU via flags Chromium |
| `UBLOCK_ENABLED=false` | `true` | Desativa o carregamento do uBlock Origin |
| `AD_BLOCKER_ENABLED=true` | `false` | Ativa o bloqueador CSS (`data/ad_selectors.txt`) |
| `HOME_URL=<url>` | `https://duckduckgo.com` | Página inicial: nova aba, botão ⌂ e restauração de sessão vazia. Editável na aba **Geral** do Settings. Lida via `env_config.get_str()`; padrão em `constants.DEFAULT_HOME_URL` |

## Dados gerados em runtime

Todos os arquivos ficam no diretório passado como argumento (ou `/tmp/bagusbagusgo_<id>/`):

| Arquivo | Conteúdo |
|---|---|
| `<base_dir>/bookmarks.json` | Favoritos |
| `<base_dir>/history.json`   | Histórico de navegação |
| `<base_dir>/session.json`   | URLs das abas para restauração |
| `<base_dir>/bagusbagusgo.log` | Log do app (stdout + stderr) |
| `<base_dir>/webengine.log` | Log de conteúdo web (console JS, CORS, etc.) |
| `<base_dir>/storage/`       | Dados persistentes do QWebEngineProfile (cookies, localStorage) |
| `<base_dir>/cache/`         | Cache HTTP do QWebEngineProfile |
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
| `UserAgentInterceptor` | Intercepta requisições HTTP por domínio (extensível) |
| `build_ad_block_js()` | Gera JS que remove elementos por seletores de `data/ad_selectors.txt` |
| `load_extensions(profile)` | Carrega extensões Chrome de `data/extensions/` via `QWebEngineExtensionManager` |

## Layout da janela

```
MainWindow  (título: "BagusBagusGo v{APP_VERSION}")
└── outer QTabWidget (7 abas)
    ├── [1] BagusBagusGo  ← browser completo
    │    ├── nav_bar (QWidget + QHBoxLayout)
    │    │    └── ← → ↻ ⌂ +  [URL bar]  ☆ ★≡ 🕐 ⬇ PT ⚙
    │    ├── bookmarks_bar (QWidget, visível só com favoritos)
    │    ├── progress_bar
    │    └── QTabWidget interno (abas das páginas web)
    ├── [2] MyAss       ← MyAssPanel
    ├── [3] AI          ← AIPanel
    ├── [4] Anonymity   (placeholder vazio)
    ├── [5] AutoBot     (placeholder vazio)
    ├── [6] Downloads   (placeholder vazio)
    └── [7] Settings    ← SettingsPanel
```

## Configurações do QWebEngineProfile

Aplicadas em `MainWindow._connect_downloads()`:

| Configuração | Valor |
|---|---|
| `ForceDarkMode` | `True` |
| `HttpUserAgent` | Aleatório a cada inicialização |
| `PersistentCookiesPolicy` | `AllowPersistentCookies` |
| `DownloadPath` | `<base_dir>/downloads/` |
| `navigator_spoof` script | Injeta em `DocumentCreation` — sobrescreve `navigator.*`, `plugins`, `mimeTypes`, `window.chrome` |
| `youtube_ad_skipper` script | Injeta em `DocumentReady` — pula propagandas automaticamente |
| `ad_blocker` script | Injeta em `DocumentReady` — remove elementos por seletor CSS (requer `AD_BLOCKER_ENABLED=true`) |
| `qwebchannel.js` | Injeta em `DocumentCreation` via `QWebEngineScript` |
| Extensões | Carregadas via `load_extensions(profile)` de `data/extensions/` |

## Comportamentos automáticos por URL

| Condição (`_on_load_finished`) | Ação |
|---|---|
| `"translate.google" in url` ou `"translate.goog" in url` | Remove a barra superior do Google Tradutor (via JS + MutationObserver) |
| YouTube (via script) | Pula propagandas a cada 500ms |

## Sessão

- `closeEvent` salva URLs de todas as abas em `session.json`
- Na inicialização, `_restore_session()` reabre as abas salvas
- Se não houver sessão, abre `HOME_URL` (padrão `https://duckduckgo.com`)

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
- Configuração de features via `.env` na raiz — nunca hardcodar flags de feature
- Novas flags de ambiente: adicionar em `env_config.get_bool()` e documentar aqui
