import random;
from pathlib import Path;

_ROOT = Path(__file__).parent.parent.parent;
_UA_FILE = _ROOT / "data" / "user_agents.txt";


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
        webdriver:           {{ get: () => undefined, configurable: true }},
        languages:           {{ get: () => ['pt-BR', 'pt', 'en-US', 'en'], configurable: true }},
        hardwareConcurrency: {{ get: () => 8, configurable: true }},
        deviceMemory:        {{ get: () => 8, configurable: true }},
    }};
    for (const [k, v] of Object.entries(props)) {{
        try {{ Object.defineProperty(navigator, k, v); }} catch(e) {{}}
    }}
    try {{ delete window.navigator.__proto__.webdriver; }} catch(e) {{}}

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
        {{ type: 'application/x-nacl',              suffixes: '',    description: 'Native Client Executable',           enabledPlugin: pluginList[2] }},
        {{ type: 'application/x-pnacl',             suffixes: '',    description: 'Portable Native Client Executable',  enabledPlugin: pluginList[2] }},
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
