import os;
import random;
import re;
from pathlib import Path;

_ROOT = Path(__file__).parent.parent.parent;
_UA_FILE = _ROOT / "data" / "user_agents.txt";

# Idiomas anunciados. A MESMA lista alimenta o header `Accept-Language` e o
# `navigator.languages` do spoof: header ausente (o padrão do QtWebEngine é vazio) ou
# divergente do JS é sinal clássico de navegador não real.
LANGUAGES       = ("pt-BR", "pt", "en-US", "en");
ACCEPT_LANGUAGE = ",".join(
    lang if i == 0 else f"{lang};q={0.9 - (i - 1) * 0.1:.1f}"
    for i, lang in enumerate(LANGUAGES)
);

# token que identifica o QtWebEngine dentro do UA montado pelo motor
_ENGINE_TOKEN = re.compile(r"\s*QtWebEngine/[\d.]+");


def random_user_agent() -> str:
    if not _UA_FILE.exists():
        _UA_FILE.parent.mkdir(parents=True, exist_ok=True);
        _UA_FILE.write_text("");
        return "";
    _MOBILE = ("Mobile", "Android", "iPhone", "iPad");
    agents = [
        line.strip() for line in _UA_FILE.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#") and not any(m in line for m in _MOBILE)
    ];
    return random.choice(agents) if agents else "";


def navigator_spoof_script(ua: str) -> str:
    if "Windows" in ua:
        platform = "Win32";
    elif "Macintosh" in ua or "Mac OS X" in ua:
        platform = "MacIntel";
    elif "iPhone" in ua:
        platform = "iPhone";
    elif "Android" in ua:
        platform = "Linux armv8l";
    else:
        platform = "Linux x86_64";

    if "Firefox" in ua:
        vendor = "";
    elif "Safari" in ua and "Chrome" not in ua:
        vendor = "Apple Computer, Inc.";
    else:
        vendor = "Google Inc.";

    is_firefox = "Firefox" in ua;
    is_chrome  = "Chrome" in ua and not is_firefox;

    # usa a contagem real de núcleos (mín. 2) para casar com o que o Chromium
    # reporta via flags — evita divergência detectável no fingerprint
    cores = max(2, os.cpu_count() or 8);

    return f"""
(function() {{
    const ua = {ua!r};
    const isChrome  = {str(is_chrome).lower()};
    const isFirefox = {str(is_firefox).lower()};

    // --- navigator básico ---
    const props = {{
        userAgent:           {{ get: () => ua, configurable: true }},
        appVersion:          {{ get: () => ua.replace('Mozilla/', ''), configurable: true }},
        vendor:              {{ get: () => {vendor!r}, configurable: true }},
        platform:            {{ get: () => {platform!r}, configurable: true }},
        webdriver:           {{ get: () => false, configurable: true }},  // Chrome real: false (não undefined)
        languages:           {{ get: () => {list(LANGUAGES)!r}, configurable: true }},
        hardwareConcurrency: {{ get: () => {cores}, configurable: true }},
        deviceMemory:        {{ get: () => 8, configurable: true }},
    }};
    for (const [k, v] of Object.entries(props)) {{
        try {{ Object.defineProperty(navigator, k, v); }} catch(e) {{}}
    }}

    // --- window.chrome (ausente no QtWebEngine, sinal forte de detecção) ---
    if (isChrome && !window.chrome) {{
        window.chrome = {{
            app: {{
                isInstalled: false,
                InstallState: {{ DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' }},
                RunningState: {{ CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }},
            }},
            runtime: {{
                OnInstalledReason: {{ CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update' }},
                OnRestartRequiredReason: {{ APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic' }},
                PlatformArch: {{ ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' }},
                PlatformNaclArch: {{ ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' }},
                PlatformOs: {{ ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win' }},
                RequestUpdateCheckStatus: {{ NO_UPDATE: 'no_update', THROTTLED: 'throttled', UPDATE_AVAILABLE: 'update_available' }},
                id: undefined,
                connect:     function() {{}},
                sendMessage: function() {{}},
            }},
            csi:       function() {{ return {{startE: Date.now(), onloadT: Date.now(), pageT: Date.now(), tran: 15}}; }},
            loadTimes: function() {{ return {{firstPaintTime: 0, firstPaintAfterLoadTime: 0, isDocumentScrollableWithoutKeyboard: true}}; }},
        }};
    }}

    // --- plugins (QtWebEngine retorna array vazio) ---
    const pluginList = [
        {{ name: 'PDF Viewer',                filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1 }},
        {{ name: 'Chrome PDF Viewer',         filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1 }},
        {{ name: 'Chromium PDF Viewer',       filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1 }},
        {{ name: 'Microsoft Edge PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1 }},
        {{ name: 'WebKit built-in PDF',       filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1 }},
    ];
    const fakePlugins = Object.assign(Object.create(null), {{
        length: pluginList.length,
        item(i)        {{ return pluginList[i] ?? null; }},
        namedItem(name){{ return pluginList.find(p => p.name === name) ?? null; }},
        refresh()      {{}},
        [Symbol.iterator]() {{ return pluginList[Symbol.iterator](); }},
    }});
    pluginList.forEach((p, i) => {{ fakePlugins[i] = p; }});
    try {{ Object.defineProperty(navigator, 'plugins', {{ get: () => fakePlugins, configurable: true }}); }} catch(e) {{}}

    // --- mimeTypes ---
    const mimeList = [
        {{ type: 'application/pdf',                 suffixes: 'pdf', description: 'Portable Document Format',          enabledPlugin: pluginList[0] }},
        {{ type: 'application/x-google-chrome-pdf', suffixes: 'pdf', description: 'Portable Document Format',          enabledPlugin: pluginList[1] }},
        {{ type: 'text/pdf',                        suffixes: 'pdf', description: 'Portable Document Format',          enabledPlugin: pluginList[2] }},
    ];
    const fakeMimes = Object.assign(Object.create(null), {{
        length: mimeList.length,
        item(i)        {{ return mimeList[i] ?? null; }},
        namedItem(type){{ return mimeList.find(m => m.type === type) ?? null; }},
        [Symbol.iterator]() {{ return mimeList[Symbol.iterator](); }},
    }});
    mimeList.forEach((m, i) => {{ fakeMimes[i] = m; }});
    try {{ Object.defineProperty(navigator, 'mimeTypes', {{ get: () => fakeMimes, configurable: true }}); }} catch(e) {{}}
}})();
""";


def engine_full_version(engine_ua: str) -> str:
    """Versão completa do Chromium embutido no QtWebEngine (ex.: "140.0.0.0").

    Lida do UA que o próprio motor monta — é a única fonte confiável, porque muda
    a cada atualização do PySide6."""
    m = re.search(r"Chrome/([\d.]+)", engine_ua);
    return m.group(1) if m else "";


def consistent_user_agent(engine_ua: str) -> str:
    """UA coerente com o motor: o UA do próprio QtWebEngine sem o token que o delata.

    Remover só o `QtWebEngine/x.y.z` devolve exatamente o UA reduzido que o Chrome
    real envia no mesmo sistema. É isso que faz logins que recusam "navegador não
    seguro" (Google) passarem: um UA da lista anuncia outro motor (Firefox) ou outra
    versão (Chrome/148 sobre motor 140), e a divergência com os Client Hints —
    que o Chromium monta a partir da versão real, não do UA — é o que denuncia."""
    return _ENGINE_TOKEN.sub("", engine_ua).strip();
