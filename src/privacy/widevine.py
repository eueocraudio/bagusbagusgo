"""Localiza o CDM do Widevine nos caminhos que o QtWebEngine procura.

O QtWebEngine **tem suporte a Widevine compilado** (conferido nos símbolos do
`libQt6WebEngineCore.so`), mas não embarca o CDM: ele varre caminhos fixos no `$HOME`. Sem o
CDM, `navigator.requestMediaKeySystemAccess("com.widevine.alpha")` falha com
`NotSupportedError` — e um Chrome sem Widevine é anomalia, além de não tocar vídeo com DRM.

Quem tem Chrome ou Firefox instalado já tem o CDM na máquina; basta ligá-lo por symlink no
caminho que o Qt procura (ver README). Aqui só detectamos, para dizer na tela o que está
valendo — nada é instalado automaticamente."""

from pathlib import Path;

_RELATIVO = "_platform_specific/linux_x64/libwidevinecdm.so";

# caminhos que o QtWebEngine varre (web_engine_library_info.cpp)
_CAMINHOS_QT = [
    Path.home() / ".config/chromium/WidevineCdm" / _RELATIVO,
    Path.home() / ".config/google-chrome/WidevineCdm" / _RELATIVO,
];

# onde o CDM costuma estar em quem já tem navegador instalado
_FONTES = [
    Path("/opt/google/chrome/WidevineCdm") / _RELATIVO,
    Path("/usr/lib/chromium/WidevineCdm") / _RELATIVO,
];


def cdm_ativo() -> Path | None:
    """Caminho do CDM que o QtWebEngine vai encontrar, ou None."""
    for p in _CAMINHOS_QT:
        if p.exists():
            return p;
    return None;


def cdm_disponivel() -> Path | None:
    """CDM presente na máquina mas fora dos caminhos do Qt (candidato a symlink)."""
    for p in _FONTES:
        if p.exists():
            return p;
    return None;
