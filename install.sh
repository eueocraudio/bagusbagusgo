#!/usr/bin/env bash
set -euo pipefail

echo "=== WebCráudio — instalação ==="

# Verifica python3
if ! command -v python3 &>/dev/null; then
    echo "Erro: python3 não encontrado. Instale o Python 3.10+ e tente novamente."
    exit 1
fi

# Instala dependências Python
echo "Instalando dependências Python..."
pip3 install --break-system-packages PySide6

# Verifica QtWebEngine (incluído no PySide6, mas verifica o import)
echo "Verificando QtWebEngine..."
python3 -c "from PySide6.QtWebEngineWidgets import QWebEngineView" \
    || { echo "Erro: QtWebEngine não disponível. Tente: pip3 install --break-system-packages PySide6[WebEngine]"; exit 1; }

# Verifica QtWebChannel
python3 -c "from PySide6.QtWebChannel import QWebChannel" \
    || { echo "Erro: QtWebChannel não disponível."; exit 1; }

# Cria diretório de dados
mkdir -p "$HOME/.config/webcraudiobot"
mkdir -p "$HOME/Downloads"

# Torna o script executável (idempotente)
chmod +x "$(dirname "$0")/install.sh"

echo ""
echo "Instalação concluída."
echo "Para iniciar: python3 run.py"
