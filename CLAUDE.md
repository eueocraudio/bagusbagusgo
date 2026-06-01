# WebCráudio — instruções para o Claude

## Visão geral

Browser desktop construído com Python 3 e PySide6 (QtWebEngine). Toda a lógica está em `src/browser.py`.

## Como rodar

```bash
python3 src/browser.py
```

## Estrutura

```
src/browser.py   — código principal (única fonte de verdade)
install.sh       — instala dependências via pip3
```

## Dados persistidos pelo usuário

| Arquivo | Conteúdo |
|---|---|
| `~/.config/webcraudiobot/bookmarks.json` | Favoritos |
| `~/.config/webcraudiobot/history.json`   | Histórico de navegação |
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

## Layout das toolbars

```
Linha 1: nav_toolbar  (ocupa 100% da largura)
          ← → ↻ ⌂ [URL bar — expansível] ☆ ★≡ 🕐 ⬇ +
Linha 2: bookmarks_toolbar  (visível apenas quando há favoritos)
```

A `nav_toolbar` fica sozinha na linha 1 graças ao `addToolBarBreak` inserido **antes** da `bookmarks_toolbar`. A barra de URL usa um `QWidget` container com `QSizePolicy.Expanding` e `addWidget(..., stretch=1)` para preencher todo o espaço disponível.

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
- Nunca usar `.parent().parent()` para navegar até `MainWindow`; usar `while not isinstance(p, MainWindow)`
