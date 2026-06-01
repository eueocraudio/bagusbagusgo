#!/usr/bin/env bash
set -euo pipefail

echo "=== BagusBagusGo v2.0.2 — instalação ==="

# Verifica python3
if ! command -v python3 &>/dev/null; then
    echo "Erro: python3 não encontrado. Instale o Python 3.10+ e tente novamente."
    exit 1
fi

# Instala dependências Python
echo "Instalando dependências Python..."
pip3 install --break-system-packages PySide6

# Verifica QtWebEngine
echo "Verificando QtWebEngine..."
python3 -c "from PySide6.QtWebEngineWidgets import QWebEngineView" \
    || { echo "Erro: QtWebEngine não disponível. Tente: pip3 install --break-system-packages PySide6[WebEngine]"; exit 1; }

# Verifica QtWebChannel
python3 -c "from PySide6.QtWebChannel import QWebChannel" \
    || { echo "Erro: QtWebChannel não disponível."; exit 1; }

# Verifica extensões estáticas
echo "Verificando extensões..."
EXTENSIONS_DIR="$(dirname "$0")/data/extensions"
if [ ! -d "$EXTENSIONS_DIR/uBlock0.chromium" ]; then
    echo "Aviso: uBlock Origin não encontrado em data/extensions/."
    echo "       Certifique-se de ter clonado o repositório completo."
else
    echo "  ✓ uBlock Origin: $(python3 -c "import json; m=json.load(open('$EXTENSIONS_DIR/uBlock0.chromium/manifest.json')); print(m['version'])")"
fi

# Cria .env a partir do exemplo se ainda não existir
SCRIPT_DIR="$(dirname "$0")"
if [ ! -f "$SCRIPT_DIR/.env" ] && [ -f "$SCRIPT_DIR/.env.example" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo "  ✓ .env criado a partir de .env.example"
fi

# Cria diretório de dados padrão
mkdir -p "$HOME/Downloads"

# Torna o script executável (idempotente)
chmod +x "$SCRIPT_DIR/install.sh"

echo ""
echo "Instalação concluída."
echo "Para iniciar: python3 run.py"
