#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_VERSION="2.0.3"

echo "=== BagusBagusGo v${APP_VERSION} — instalação ==="

# Verifica python3
if ! command -v python3 &>/dev/null; then
    echo "Erro: python3 não encontrado. Instale o Python 3.10+ e tente novamente."
    exit 1
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python detectado: ${PY_VERSION}"

# Instala dependências de sistema necessárias para Qt/WebEngine
echo "Instalando dependências de sistema..."
apt-get install -y \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libnss3 \
    libnspr4 \
    libasound2t64 \
    libgbm1 \
    libdrm2 \
    libxss1 \
    libxtst6 2>&1 | grep -E "^(Setting up|Err|E:)" || true
echo "  ✓ Dependências de sistema OK"

# Determina como instalar pip — como o usuário real, não como root
if [ -n "${SUDO_USER:-}" ]; then
    PIP_CMD="runuser $SUDO_USER -c"
    PIP_ARGS="pip3 install -r '$SCRIPT_DIR/requirements.txt' --break-system-packages"
    PYTHON_CMD="runuser $SUDO_USER -c"
else
    PIP_CMD="bash -c"
    PIP_ARGS="pip3 install -r '$SCRIPT_DIR/requirements.txt' --break-system-packages"
    PYTHON_CMD="bash -c"
fi

# Instala dependências Python para o usuário correto
echo "Instalando dependências Python..."
$PIP_CMD "$PIP_ARGS"

# Verifica QtWebEngine e QtWebChannel como o usuário correto
echo "Verificando QtWebEngine..."
$PYTHON_CMD "python3 -c 'from PySide6.QtWebEngineWidgets import QWebEngineView'" \
    || { echo "Erro: QtWebEngine não disponível. Tente: pip3 install --break-system-packages PySide6[WebEngine]"; exit 1; }

$PYTHON_CMD "python3 -c 'from PySide6.QtWebChannel import QWebChannel'" \
    || { echo "Erro: QtWebChannel não disponível."; exit 1; }

echo "  ✓ PySide6 + QtWebEngine + QtWebChannel OK"

# Verifica extensões estáticas
echo "Verificando extensões..."
EXTENSIONS_DIR="$SCRIPT_DIR/data/extensions"
if [ ! -d "$EXTENSIONS_DIR/uBlock0.chromium" ]; then
    echo "  Aviso: uBlock Origin não encontrado em data/extensions/."
    echo "         Certifique-se de ter clonado o repositório completo."
else
    UBLOCK_VERSION=$(python3 -c "import json; m=json.load(open('$EXTENSIONS_DIR/uBlock0.chromium/manifest.json')); print(m['version'])")
    echo "  ✓ uBlock Origin: ${UBLOCK_VERSION}"
fi

# Cria .env a partir do exemplo se ainda não existir
if [ ! -f "$SCRIPT_DIR/.env" ] && [ -f "$SCRIPT_DIR/.env.example" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo "  ✓ .env criado a partir de .env.example"
fi

# Instala o app para o usuário (requer sudo)
if [ -n "${SUDO_USER:-}" ]; then
    USER_HOME="/home/$SUDO_USER"
    INSTALL_DIR="$USER_HOME/.local/bin/bagus"
    APPS_DIR="$USER_HOME/.local/share/applications"
    APPS_BAGUS_DATA="$USER_HOME/.local/data/bagus"

    runuser "$SUDO_USER" -c "mkdir -p '$INSTALL_DIR' '$APPS_DIR' '$APPS_BAGUS_DATA'"

    cp -r "$SCRIPT_DIR"/. "$INSTALL_DIR/"
    cp "$INSTALL_DIR/resources/bagus.desktop" "$APPS_DIR/"
    cp "$SCRIPT_DIR/bagus" /bin/bagus
    chmod +x /bin/bagus

    echo "  ✓ Instalado em $INSTALL_DIR"
    echo "  ✓ Atalho de desktop registrado"
    echo "  ✓ Comando 'bagus' disponível em /bin/bagus"
else
    echo "  Aviso: não executado com sudo — etapas de instalação do sistema ignoradas."
    echo "         Execute 'sudo bash install.sh' para instalar o comando 'bagus' e o ícone de desktop."
fi

echo ""
echo "Instalação concluída."
echo "Para iniciar: python3 run.py   ou   bagus"
