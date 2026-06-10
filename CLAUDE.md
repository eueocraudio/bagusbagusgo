# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# BagusBagusGo (BBGo) — instruções para o Claude

## Versão atual

**v2.1.0** — constantes em `src/utils/constants.py` (`APP_NAME`, `APP_VERSION`, `APP_ID`).

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

O código em `src/` é organizado em subpacotes por domínio (cada um com `__init__.py`). Imports usam caminhos relativos ao pacote (ex.: `from .settings import env_config`, `from ..utils.constants import ...`).

```
run.py                      — entry point; passa sys.argv para main()
bagus                       — launcher shell (usado após instalação)
requirements.txt            — dependências (PySide6)
.env / .env.example         — config de features (ver seção .env)
data/
  user_agents.txt           — lista de user agents (um por linha)
  ad_selectors.txt          — seletores CSS pessoais (lista local)
  ad_selectors_web.txt      — seletores CSS baixados da internet (via Update)
  extensions/
    uBlock0.chromium/       — extensão uBlock Origin estática
src/
  browser.py                — main(args): lê args, carrega .env, aplica flags Chromium/ZOOM, inicia MainWindow
  main_window.py            — MainWindow (orquestra tudo)
  utils/
    constants.py            — APP_NAME, APP_VERSION, APP_ID, HISTORY_MAX, DEFAULT_HOME_URL
    theme.py                — DARK_STYLESHEET (dark + vermelho)
    logger.py               — setup(base_dir): logger do app (bbgo) + logger web (bbgo.web); web_logger()
    tasks.py                — run_async(fn, ...): executor sobre QThreadPool; resultado volta na thread de UI via signals
    async_io.py             — writer(): grava JSON fora da thread de UI (thread dedicada, coalescing + escrita atômica + flush())
  core/
    browser_tab.py          — BrowserTab (QWebEngineView, recebe add_tab como callback) + LoggingWebEnginePage
    click_capture.py        — ClickCapture + CLICK_LISTENER_JS
    session_manager.py      — SessionManager: salva/restaura URLs das abas
    zoom_manager.py         — ZoomManager: zoom da página web por página/URL (zoom.json)
    extension_manager.py    — load_extensions(profile): carrega extensões de data/extensions/
  privacy/
    user_agent.py           — random_user_agent(), navigator_spoof_script(ua)
    ad_blocker.py           — build_ad_block_js(): JS das listas pessoal + web
    ads_updater.py          — update(): baixa/atualiza data/ad_selectors_web.txt
    ua_updater.py           — update(): baixa/atualiza data/user_agents.txt
  bookmarks/
    bookmark_manager.py     — BookmarkManager (CRUD JSON)
    bookmarks_dialog.py     — ManageBookmarksDialog
  history/
    history_manager.py      — HistoryManager (registro e busca, máx. 5000)
    history_dialog.py       — HistoryDialog
  downloads/
    download_panel.py       — DownloadItemWidget + DownloadPanel
  settings/
    env_config.py           — carrega .env (4 níveis); get_bool(key, default), get_str(key, default), get_int(key, default)
    settings_panel.py       — SettingsPanel (aba Settings: Geral, Ad Selectors, WebSettings...)
    websettings_manager.py  — aplica/persiste QWebEngineSettings no profile (websettings.json)
  myass/
    panel.py                — MyAssPanel (barra de botões + tabela 4 colunas)
  ai/
    panel.py                — AIPanel
install.sh                  — instala dependências e registra o app (requer sudo)
resources/
  bagus.desktop             — arquivo .desktop para o menu de aplicativos
  bagus.png                 — ícone do app
```

## Configuração via `.env`

O arquivo `.env` é carregado automaticamente por `src/settings/env_config.py` antes de qualquer outra inicialização. Carregamento em 4 níveis (cada um sobrescreve o anterior): `.env` do projeto → `~/.env` → `~/.local/bin/bagus/.env` → `<base_dir>/.env`. **Variáveis exportadas no shell sempre vencem** (`_SHELL_VARS`). Variáveis disponíveis:

| Variável | Padrão | Efeito |
|---|---|---|
| `WEBGL_FORCE=true` | `false` | Força WebGL/GPU via flags Chromium |
| `UBLOCK_ENABLED=false` | `true` | Desativa o carregamento do uBlock Origin |
| `AD_BLOCKER_ENABLED=true` | `false` | Ativa o bloqueador CSS por seletores |
| `AD_SELECTOR_PERSONAL_ENABLED=false` | `true` | Usa a lista pessoal (`data/ad_selectors.txt`) |
| `AD_SELECTOR_WEB_ENABLED=true` | `false` | Usa a lista baixada da internet (`data/ad_selectors_web.txt`) |
| `ZOOM=<int>` | `1` | Incremento (em pt) na fonte de todos os widgets; `0` = padrão do sistema |
| `HOME_URL=<url>` | `https://duckduckgo.com` | Página inicial: nova aba, botão ⌂ e restauração de sessão vazia. Editável na aba **Geral** do Settings. Lida via `env_config.get_str()`; padrão em `constants.DEFAULT_HOME_URL` |
| `MULTITHREAD_ENABLED=false` | `true` | Liga flags de multithreading do Chromium (site-per-process, GPU rasterization, zero-copy, raster threads, ParallelDownloading) em `browser._apply_chromium_flags()` |
| `CHROMIUM_RASTER_THREADS=<int>` | `min(cpu, 4)` | Número de threads de rasterização do Chromium (`--num-raster-threads`); só tem efeito com `MULTITHREAD_ENABLED=true` |

## Dados gerados em runtime

Todos os arquivos ficam no diretório passado como argumento (ou `/tmp/bagusbagusgo_<id>/`):

| Arquivo | Conteúdo |
|---|---|
| `<base_dir>/bookmarks.json` | Favoritos |
| `<base_dir>/history.json`   | Histórico de navegação |
| `<base_dir>/session.json`   | URLs das abas para restauração |
| `<base_dir>/zoom.json`      | Fator de zoom por página/URL, ignorando o fragmento `#` (restaurado ao revisitar/voltar) |
| `<base_dir>/websettings.json` | Overrides de `QWebEngineSettings` (aba WebSettings) |
| `<base_dir>/bagusbagusgo.log` | Log do app (stdout + stderr) |
| `<base_dir>/webengine.log` | Log de conteúdo web (console JS, CORS, etc.) |
| `<base_dir>/storage/`       | Dados persistentes do QWebEngineProfile (cookies, localStorage) |
| `<base_dir>/cache/`         | Cache HTTP do QWebEngineProfile |
| `<base_dir>/downloads/`     | Arquivos baixados |

## Threading

O app usa a thread de UI do Qt para tudo que toca widgets/QtWebEngine (regra do Qt) e
empurra trabalho bloqueante para fora dela:

- **`utils/tasks.run_async()`** — roda funções bloqueantes (ex.: updaters de rede) sobre o
  `QThreadPool` global; `result`/`error`/`finished` voltam na thread de UI via signals
  (conexões enfileiradas). Usado por `SettingsPanel` no botão **Update**.
- **`utils/async_io.writer()`** — thread dedicada que grava todos os JSON de runtime
  (`bookmarks`, `history`, `session`, `zoom`, `websettings`) fora da thread de UI, com
  coalescing por caminho (última gravação vence) e escrita atômica (`.tmp` + `replace`).
  `MainWindow.closeEvent` chama `writer().flush()` para garantir persistência antes de sair.
- **`ua_updater.update()`** — busca as fontes de user agent em paralelo (`ThreadPoolExecutor`).
- **Chromium/QWebEnginePage** — a execução das páginas roda nos processos/threads do próprio
  Chromium (não há API Python para threadeá-las). O paralelismo é maximizado por flags em
  `browser._apply_chromium_flags()` (ver `MULTITHREAD_ENABLED`): `--site-per-process` coloca
  cada site em seu próprio render process, além de rasterização em GPU/threads e downloads
  paralelos.

## Arquitetura — classes principais

| Classe / módulo | Responsabilidade |
|---|---|
| `BookmarkManager` | CRUD de favoritos em JSON |
| `ManageBookmarksDialog` | Diálogo para renomear/remover favoritos |
| `HistoryManager` | Registro e busca de histórico |
| `HistoryDialog` | Diálogo com busca, agrupamento por data e limpeza |
| `SessionManager` | Salva URLs no `closeEvent`; restaura na inicialização |
| `ZoomManager` | Persiste o fator de zoom por página/URL (chave = URL sem fragmento) em `zoom.json`; reaplica em `_on_url_changed` e `_on_load_finished`. Entrada: **Ctrl+scroll** (cada `BrowserTab` filtra só o próprio widget de renderização via `childEvent`/`eventFilter` → callback `on_ctrl_wheel` → `MainWindow._on_ctrl_wheel`) e atalhos Ctrl+ / Ctrl- / Ctrl+0. **Não** instalar event filter na `QApplication` inteira — causa segfault na init do WebEngine |
| `ClickCapture` | `QObject` com `@Slot` — recebe cliques via `QWebChannel` → `print()` |
| `DownloadItemWidget` | Widget de progresso por arquivo baixado |
| `DownloadPanel` | `QDockWidget` inferior com lista de downloads |
| `BrowserTab` | `QWebEngineView`; recebe `add_tab` como callback |
| `MainWindow` | Janela principal — orquestra tudo |
| `MyAssPanel` | Painel da aba MyAss: barra de botões (New work, New flow) + tabela Work/Flow/Status/Date |
| `AIPanel` | Painel da aba AI |
| `SettingsPanel` | Aba Settings: sub-abas Geral (HOME_URL), Ad Selectors, WebSettings; aciona os updaters via `tasks.run_async()` |
| `websettings_manager` | Carrega/aplica/persiste overrides de `QWebEngineSettings` em `websettings.json` (grava via `async_io.writer()`) |
| `tasks.run_async()` | Executor sobre `QThreadPool`; entrega `result`/`error`/`finished` na thread de UI |
| `async_io.writer()` | Gravador JSON assíncrono (thread dedicada, coalescing, escrita atômica, `flush()`) |
| `DARK_STYLESHEET` | Stylesheet global dark + vermelho aplicado no `QApplication` |
| `random_user_agent()` | Lê `data/user_agents.txt` e retorna UA aleatório |
| `navigator_spoof_script(ua)` | Gera JS que sobrescreve `navigator.*` para mascarar QtWebEngine |
| `build_ad_block_js()` | Gera JS que remove elementos pelas listas pessoal/web de seletores |
| `ads_updater.update()` / `ua_updater.update()` | Baixam/atualizam `ad_selectors_web.txt` e `user_agents.txt` |
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

- Todo código novo vai em `src/`, dentro do subpacote de domínio adequado (`core`, `privacy`, `bookmarks`, `history`, `downloads`, `settings`, `utils`, `myass`, `ai`) — criar novo subpacote (com `__init__.py`) se nenhum couber
- Usar imports relativos ao pacote (`from ..utils.constants import ...`), nunca caminhos absolutos com `src.`
- Usar PySide6 para qualquer elemento de interface
- Terminar instruções Python com `;`
- Usar 4 espaços para indentação (nunca TAB)
- Não usar `QApplication.exec_()` — usar `app.exec()`
- Motor de busca: DuckDuckGo (`https://duckduckgo.com/?q=`)
- `BrowserTab` recebe `add_tab` como callback — não importa `MainWindow`
- Barras de navegação/favoritos são `QWidget` + `QHBoxLayout`, não `QToolBar`
- Versão centralizada em `src/utils/constants.py` — nunca hardcodar em outro lugar
- User agents em `data/user_agents.txt` — um por linha
- Tema em `src/utils/theme.py` — editar `DARK_STYLESHEET` para mudar cores
- Configuração de features via `.env` na raiz — nunca hardcodar flags de feature
- Novas flags de ambiente: adicionar em `src/settings/env_config.py` (`get_bool()`/`get_str()`/`get_int()`) e documentar na tabela `.env` acima
- Trabalho bloqueante (rede/disco/parsing) nunca roda na thread de UI: usar `utils.tasks.run_async()` para tarefas pontuais e `utils.async_io.writer()` para persistência JSON; nunca tocar widgets ou objetos QtWebEngine fora da thread de UI
