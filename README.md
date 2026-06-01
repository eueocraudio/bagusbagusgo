# BagusBagusGo

Browser desktop construído com Python 3 e PySide6 (QtWebEngine).  
Motor de busca padrão: **DuckDuckGo** · Tema: **Dark + Vermelho**.

**Repositório:** https://github.com/eueocraudio/bagusbagusgo

![Screenshot](docs/screenshot.png)

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
# Diretório temporário gerado automaticamente em /tmp/
python3 run.py

# Diretório específico para dados persistentes
python3 run.py /caminho/do/diretorio
```

O caminho do diretório de dados é impresso no terminal ao iniciar.

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

### 2. Abas de páginas web

| Ação | Como fazer |
|---|---|
| Abrir nova aba | Botão `+` na barra ou **Ctrl+T** |
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
| Parar carregamento | Botão `✕` (durante carregamento) ou **F5** |
| Página inicial | Botão `⌂` (abre DuckDuckGo) |
| Focar barra de endereço | **Ctrl+L** |

---

### 4. Favoritos

1. Navegue até a página e pressione **Ctrl+D** ou clique em `☆`
2. O botão muda para `★` — favorito salvo
3. A **barra de favoritos** aparece abaixo da barra de navegação
4. Clique em qualquer favorito para navegar direto

**Gerenciar** (`★≡`): renomear (duplo-clique) e remover favoritos.  
**Remover favorito atual**: pressione **Ctrl+D** novamente.

---

### 5. Histórico

1. Pressione **Ctrl+H** ou clique em `🕐`
2. Entradas agrupadas por **Hoje**, **Ontem** e datas anteriores
3. Pesquisa em tempo real por título ou URL
4. Duplo-clique numa entrada para navegar
5. "Limpar tudo" apaga todo o histórico (pede confirmação)

---

### 6. Downloads

1. Clique em qualquer link de download
2. O **painel de downloads** abre automaticamente na parte inferior
3. Progresso, velocidade e tamanho em tempo real
4. Após concluir: **Abrir** (arquivo) ou **Pasta** (`<base_dir>/downloads/`)
5. "Limpar concluídos" remove os itens finalizados do painel

Abrir/fechar manualmente: botão `⬇` ou **Ctrl+J**.

---

### 7. Settings (`⚙`)

Botão na extremidade direita da barra de navegação. Menu suspenso com:

- **About** — informações sobre o BagusBagusGo

---

### 8. Tema Dark

Toda a interface usa o tema escuro definido em `src/theme.py`:
- Fundo `#1a1a1a`, texto `#e0e0e0`
- Acentos em vermelho `#c0392b` em linhas, bordas, abas ativas e scrollbars
- Páginas web também em dark mode via `QWebEngineSettings.ForceDarkMode`

---

### 9. User Agent aleatório

A cada inicialização, um User Agent é sorteado de `data/user_agents.txt` e aplicado em todas as requisições. O UA escolhido é impresso no terminal:

```
[bagusbagusgo] user-agent: Mozilla/5.0 (X11; Linux x86_64) ...
```

Para adicionar ou remover agentes, edite `data/user_agents.txt` — uma linha por agente.

---

### 10. Captura de cliques via Python

Todo elemento clicado tem seu `tag`, `id` e `name` impressos no terminal:

```
[clique] tag=<a>,  id="logo"
[clique] tag=<input>,  name="q"
[clique] tag=<button>,  id="btnK"
```

---

### 11. Injeção de JavaScript por URL

Em `src/main_window.py`, no método `_on_load_finished`, adicione:

```python
if "site.com" in url:
    view.page().runJavaScript("document.title = 'Meu título';");
```

**Regra ativa:** qualquer URL com `google.com` é redirecionada para o DuckDuckGo.

---

## Atalhos

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

## Interface — abas externas

| # | Aba | Conteúdo |
|---|---|---|
| 1 | **BagusBagusGo** | Browser completo |
| 2 | **MyAss** | Barra de botões (New work, New flow) + tabela 4 colunas |
| 3 | **Anonymity** | — |
| 4 | **AutoBot** | — |
| 5 | **Downloads** | — |

---

## Dados gerados

Todos os arquivos ficam no diretório passado como argumento:

| Localização | Conteúdo |
|---|---|
| `<base_dir>/bookmarks.json` | Favoritos |
| `<base_dir>/history.json` | Histórico (máx. 5000 entradas) |
| `<base_dir>/downloads/` | Arquivos baixados |

---

## Estrutura do projeto

```
run.py                    — entry point
data/
  user_agents.txt         — lista de user agents
src/
  browser.py              — main()
  constants.py            — constantes globais
  theme.py                — tema dark + vermelho
  user_agent.py           — seleção aleatória de user agent
  bookmark_manager.py     — gerenciamento de favoritos
  bookmarks_dialog.py     — diálogo de favoritos
  history_manager.py      — gerenciamento de histórico
  history_dialog.py       — diálogo de histórico
  download_panel.py       — painel de downloads
  click_capture.py        — captura de cliques via QWebChannel
  browser_tab.py          — aba do browser
  main_window.py          — janela principal
  myass/
    __init__.py
    panel.py              — MyAssPanel
install.sh                — script de instalação
CLAUDE.md                 — instruções para o Claude Code
README.md                 — esta documentação
.gitignore                — arquivos ignorados pelo git
```
