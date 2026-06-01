# WebCráudio

Browser desktop construído com Python 3 e PySide6 (QtWebEngine).  
Motor de busca padrão: **DuckDuckGo**.

---

## Requisitos

- Python 3.10 ou superior
- PySide6 com QtWebEngine e QtWebChannel

---

## Instalação

```bash
bash install.sh
```

Ou manualmente:

```bash
pip3 install --break-system-packages PySide6
```

---

## Iniciando o browser

```bash
python3 run.py
```

---

## Tutorial

### 1. Navegar para um site

Digite na barra de endereço e pressione **Enter**:

- URL com domínio → abre diretamente
  ```
  python.org
  https://github.com
  ```
- Texto com espaços → pesquisa no DuckDuckGo
  ```
  como instalar python no linux
  ```

---

### 2. Abas

| Ação | Como fazer |
|---|---|
| Abrir nova aba | Botão `+` na toolbar ou **Ctrl+T** |
| Fechar aba atual | Botão `✕` na aba ou **Ctrl+W** |
| Trocar de aba | Clique na aba desejada |
| Reordenar abas | Arraste a aba para a posição desejada |

---

### 3. Navegação

| Ação | Como fazer |
|---|---|
| Voltar | Botão `←` ou **Alt+←** |
| Avançar | Botão `→` ou **Alt+→** |
| Recarregar | Botão `↻` ou **F5** |
| Parar carregamento | Botão `✕` (aparece durante o carregamento) ou **F5** |
| Ir para a página inicial | Botão `⌂` (abre o DuckDuckGo) |
| Focar na barra de endereço | **Ctrl+L** |

---

### 4. Favoritos

1. Navegue até a página que deseja salvar
2. Clique no botão `☆` na toolbar ou pressione **Ctrl+D**
3. O botão muda para `★` — a página está salva
4. A **barra de favoritos** aparece automaticamente abaixo da toolbar de navegação
5. Clique em qualquer favorito para navegar direto

**Gerenciar favoritos** (`★≡`):
- Renomear: selecione o item e clique em "Renomear" (ou duplo-clique)
- Remover: selecione o item e clique em "Remover"

Para **remover um favorito** da página atual: clique em `★` ou pressione **Ctrl+D** novamente.

---

### 5. Histórico

1. Pressione **Ctrl+H** ou clique em `🕐` na toolbar
2. O diálogo exibe as visitas agrupadas por **Hoje**, **Ontem** e datas anteriores
3. **Pesquisar**: digite na barra de busca — filtra por título ou URL em tempo real
4. **Abrir**: selecione uma entrada e clique em "Abrir" (ou duplo-clique) para navegar
5. **Remover entrada**: selecione e clique em "Remover entrada"
6. **Limpar tudo**: clique em "Limpar tudo" e confirme

---

### 6. Downloads

1. Clique em qualquer link de download em uma página
2. O **painel de downloads** abre automaticamente na parte inferior da janela
3. Acompanhe o progresso, velocidade e tamanho em tempo real
4. Após concluir:
   - **Abrir**: abre o arquivo com o programa padrão do sistema
   - **Pasta**: abre a pasta `~/Downloads/` no gerenciador de arquivos
5. "Limpar concluídos" remove do painel os itens finalizados

Para abrir/fechar o painel manualmente: botão `⬇` na toolbar ou **Ctrl+J**.

---

### 7. Captura de cliques via Python

O browser captura automaticamente o `id` e o `name` de todo elemento clicado e imprime no terminal:

```
[clique] tag=<a>,  id="logo"
[clique] tag=<input>,  name="q"
[clique] tag=<button>,  id="btnK"
```

Útil para inspecionar a estrutura de páginas sem abrir o DevTools.

---

### 8. Injeção de JavaScript por URL

Em `src/browser.py`, no método `_on_load_finished`, é possível executar JavaScript arbitrário sempre que uma URL específica carregar:

```python
if "exemplo.com" in url:
    view.page().runJavaScript("document.title = 'Meu título';");
```

**Exemplos de uso:**

```python
# Alterar um elemento pelo seletor CSS
view.page().runJavaScript(
    "var h1 = document.querySelector('h1');"
    "if (h1) { h1.textContent = 'Novo título'; }"
);

# Localizar elemento por XPath e clicar
view.page().runJavaScript(
    "var result = document.evaluate('/html/body/div[1]', document, null,"
    "  XPathResult.FIRST_ORDERED_NODE_TYPE, null);"
    "var el = result.singleNodeValue;"
    "if (el) { el.click(); }"
);

# Aguardar N segundos e clicar em um link
view.page().runJavaScript(
    "setTimeout(function() {"
    "  var link = document.querySelector('a');"
    "  if (link) { link.click(); }"
    "}, 3000);"
);

# Redirecionar para outro site
view.page().runJavaScript("window.location.href = 'https://duckduckgo.com';");
```

**Regra ativa:** ao entrar em qualquer URL com `google.com`, o browser redireciona automaticamente para o DuckDuckGo.

---

## Atalhos — resumo

| Atalho | Ação |
|---|---|
| Ctrl+T | Nova aba |
| Ctrl+W | Fechar aba |
| Ctrl+L | Foco na barra de endereço |
| Ctrl+D | Adicionar / remover favorito |
| Ctrl+H | Abrir histórico |
| Ctrl+J | Abrir / fechar painel de downloads |
| F5 | Recarregar / parar |
| Alt+← | Voltar |
| Alt+→ | Avançar |

---

## Dados do usuário

| Localização | Conteúdo |
|---|---|
| `~/.config/webcraudiobot/bookmarks.json` | Favoritos |
| `~/.config/webcraudiobot/history.json` | Histórico (máx. 5000 entradas) |
| `~/Downloads/` | Arquivos baixados |

---

## Estrutura do projeto

```
run.py                    — entry point
src/
  browser.py              — main()
  constants.py            — constantes globais
  bookmark_manager.py     — gerenciamento de favoritos
  bookmarks_dialog.py     — diálogo de favoritos
  history_manager.py      — gerenciamento de histórico
  history_dialog.py       — diálogo de histórico
  download_panel.py       — painel de downloads
  click_capture.py        — captura de cliques via QWebChannel
  browser_tab.py          — aba do browser
  main_window.py          — janela principal
install.sh                — script de instalação
CLAUDE.md                 — instruções para o Claude Code
README.md                 — esta documentação
.gitignore                — arquivos ignorados pelo git
```
