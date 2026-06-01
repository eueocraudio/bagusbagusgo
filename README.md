# BagusBagusGo (BBGo)

**Versão: 2.0.1**  
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

## Iniciando

```bash
# Diretório temporário em /tmp/ (gerado automaticamente)
python3 run.py

# Diretório específico para dados persistentes
python3 run.py /caminho/do/diretorio
```

O caminho do diretório de dados é impresso no terminal:
```
[BBGo v2.0.1] diretório de dados: /tmp/bagusbagusgo_abc123
```

---

## Tutorial

### 1. Navegar para um site

Digite na barra de endereço e pressione **Enter**:

- URL com domínio → abre diretamente: `python.org`, `https://github.com`
- Texto com espaços → pesquisa no DuckDuckGo: `como instalar python no linux`

---

### 2. Abas de páginas web

| Ação | Como fazer |
|---|---|
| Abrir nova aba | Botão `+` ou **Ctrl+T** |
| Fechar aba | Botão `✕` na aba ou **Ctrl+W** |
| Trocar de aba | Clique na aba desejada |
| Reordenar abas | Arraste a aba |

Ao fechar uma aba com vídeo/áudio em reprodução, a mídia é pausada automaticamente.

---

### 3. Navegação

| Ação | Como fazer |
|---|---|
| Voltar | `←` ou **Alt+←** |
| Avançar | `→` ou **Alt+→** |
| Recarregar | `↻` ou **F5** |
| Parar | `✕` (durante carregamento) ou **F5** |
| Página inicial | `⌂` (abre DuckDuckGo) |
| Foco na barra | **Ctrl+L** |

---

### 4. Restauração de sessão

O browser salva automaticamente as URLs abertas ao fechar.  
Na próxima abertura, todas as abas são restauradas.

---

### 5. Favoritos

1. Pressione **Ctrl+D** ou clique em `☆` para favoritar
2. O botão muda para `★` — favorito salvo
3. A **barra de favoritos** aparece abaixo da barra de navegação
4. Clique em qualquer favorito para navegar direto

**Gerenciar** (`★≡`): renomear (duplo-clique) e remover.  
**Remover favorito atual**: **Ctrl+D** novamente.

---

### 6. Histórico

1. **Ctrl+H** ou `🕐` — abre o diálogo
2. Entradas agrupadas por **Hoje**, **Ontem** e datas anteriores
3. Pesquisa em tempo real por título ou URL
4. Duplo-clique para navegar; "Limpar tudo" apaga o histórico

---

### 7. Downloads

1. Clique em qualquer link de download
2. O **painel de downloads** abre automaticamente na parte inferior
3. Progresso, velocidade e tamanho em tempo real
4. Após concluir: **Abrir** (arquivo) ou **Pasta** (`<base_dir>/downloads/`)

Abrir/fechar manualmente: `⬇` ou **Ctrl+J**.

---

### 8. Settings (`⚙`)

Botão na extremidade direita da barra. Menu com:
- **About** — nome, versão e informações do app

---

### 9. Tema Dark

Interface escura com acentos vermelhos (`src/theme.py`).  
Páginas web também em dark mode via `QWebEngineSettings.ForceDarkMode`.

---

### 10. User Agent aleatório

A cada inicialização, um User Agent é sorteado de `data/user_agents.txt`:

```
[BBGo v2.0.1] user-agent: Mozilla/5.0 (X11; Linux x86_64) ...
```

O `navigator.*`, `plugins`, `mimeTypes` e `window.chrome` são spoofados para mascarar o QtWebEngine.

---

### 11. Pular propagandas no YouTube

Ao acessar qualquer página do YouTube, um script roda a cada 500ms:
- Clica automaticamente no botão "Pular" quando disponível
- Se a propaganda for não pulável, avança o vídeo para o fim

---

### 12. Captura de cliques via Python

Todo elemento clicado tem `tag`, `id` e `name` impressos no terminal:

```
[clique] tag=<a>,  id="logo"
[clique] tag=<input>,  name="q"
```

---

### 13. Injeção de JavaScript por URL

Em `src/main_window.py`, método `_on_load_finished`:

```python
if "site.com" in url:
    view.page().runJavaScript("document.title = 'Meu título';");
```

**Regra ativa:** URLs com `google.com` são redirecionadas para o DuckDuckGo.

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
| 2 | **MyAss** | Barra de botões (New work, New flow) + tabela Work/Flow/Status/Date |
| 3 | **Anonymity** | — |
| 4 | **AutoBot** | — |
| 5 | **Downloads** | — |

---

## Dados gerados

| Localização | Conteúdo |
|---|---|
| `<base_dir>/bookmarks.json` | Favoritos |
| `<base_dir>/history.json` | Histórico (máx. 5000 entradas) |
| `<base_dir>/session.json` | URLs das abas (restauração) |
| `<base_dir>/downloads/` | Arquivos baixados |

---

## Estrutura do projeto

```
run.py                      — entry point
data/
  user_agents.txt           — lista de user agents
src/
  browser.py                — main()
  constants.py              — APP_NAME, APP_VERSION, APP_ID e constantes globais
  theme.py                  — tema dark + vermelho
  user_agent.py             — user agent aleatório + navigator spoof
  request_interceptor.py    — interceptor HTTP por domínio (extensível)
  session_manager.py        — salva/restaura sessão
  bookmark_manager.py       — gerenciamento de favoritos
  bookmarks_dialog.py       — diálogo de favoritos
  history_manager.py        — gerenciamento de histórico
  history_dialog.py         — diálogo de histórico
  download_panel.py         — painel de downloads
  click_capture.py          — captura de cliques via QWebChannel
  browser_tab.py            — aba do browser
  main_window.py            — janela principal
  myass/
    __init__.py
    panel.py                — MyAssPanel
install.sh                  — script de instalação
CLAUDE.md                   — instruções para o Claude Code
README.md                   — esta documentação
.gitignore                  — arquivos ignorados pelo git
```
