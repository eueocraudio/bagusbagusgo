from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor;


YOUTUBE_UA = b"Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0";

_RULES: list[tuple[str, bytes]] = [
    ("youtube.com", YOUTUBE_UA),
];

YOUTUBE_SPOOF_JS = """
(function() {
    if (!window.location.hostname.includes('youtube.com')) return;

    const ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0';

    const navOverrides = {
        userAgent:  ua,
        appVersion: ua.replace('Mozilla/', ''),
        vendor:     '',
        platform:   'Linux x86_64',
        webdriver:  undefined,
        productSub: '20100101',
        product:    'Gecko',
        oscpu:      'Linux x86_64',
        appName:    'Netscape',
    };

    for (const [k, v] of Object.entries(navOverrides)) {
        try {
            Object.defineProperty(navigator, k, { get: () => v, configurable: true });
        } catch(e) {}
    }

    // Firefox não tem window.chrome
    try {
        Object.defineProperty(window, 'chrome', { get: () => undefined, configurable: true });
    } catch(e) {}

    // Remove rastros de webdriver
    try { delete navigator.__proto__.webdriver; } catch(e) {}
    try { delete Object.getPrototypeOf(navigator).webdriver; } catch(e) {}

    // Spoofa permissions API
    if (navigator.permissions) {
        const _query = navigator.permissions.query.bind(navigator.permissions);
        navigator.permissions.query = (p) => {
            if (p.name === 'notifications') {
                return Promise.resolve({ state: 'denied', onchange: null });
            }
            return _query(p);
        };
    }

    // Linguagens coerentes com Firefox/Linux
    Object.defineProperty(navigator, 'languages', {
        get: () => ['pt-BR', 'pt', 'en-US', 'en'],
        configurable: true,
    });
})();
""";


class UserAgentInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString();
        for domain, ua in _RULES:
            if domain in url:
                info.setHttpHeader(b"User-Agent", ua);
                return;
