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
| `BrowserTab` | `QWebEngineView` com suporte a abertura de links em nova aba |
| `MainWindow` | Janela principal: toolbars, abas, atalhos, orquestra tudo |

## Funcionalidades implementadas

- Navegação com múltiplas abas (Ctrl+T / Ctrl+W)
- Barra de endereço com busca automática no DuckDuckGo
- Favoritos persistidos com barra de acesso rápido (Ctrl+D)
- Histórico de navegação com busca e limpeza (Ctrl+H)
- Downloads com painel de progresso, velocidade e abertura do arquivo (Ctrl+J)
- Captura de cliques em tags HTML via `QWebChannel` → `print()` no Python
- Injeção de JavaScript por URL no método `_on_load_finished`

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
- `google.com` → redireciona para `https://duckduckgo.com` via `window.location.href`

## Regras de desenvolvimento

- Todo código novo vai em `src/`
- Usar PySide6 para qualquer elemento de interface
- Terminar instruções Python com `;`
- Usar 4 espaços para indentação (nunca TAB)
- Não usar `QApplication.exec_()` (deprecated); usar `app.exec()`
- Motor de busca padrão: DuckDuckGo (`https://duckduckgo.com/?q=`)
- Página inicial e botão home: `https://duckduckgo.com`
- Ao adicionar nova regra de JS por URL, documentar em "Regras ativas no momento" acima
