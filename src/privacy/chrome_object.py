"""Completa o `window.chrome` — o único objeto onde o Chrome real tem propriedades próprias.

Medido contra o Chrome instalado nesta máquina: `Object.getOwnPropertyNames(window.chrome)`
devolve `["app", "csi", "loadTimes"]`. O QtWebEngine cria o `window.chrome` **vazio**, e um
Chrome sem `loadTimes`/`csi` é anomalia conhecida de navegador embutido.

Por que isto é seguro e o spoof de `navigator` não era: aqui as propriedades próprias são
exatamente as que o Chrome tem ali. Já em `navigator` o Chrome real não tem **nenhuma** própria
(tudo vive no protótipo), então qualquer `defineProperty` no objeto denuncia o patch."""

CHROME_OBJECT_JS = """
(function() {
    if (!window.chrome || window.chrome.loadTimes) return;
    const agora = () => Date.now() / 1000;
    try {
        window.chrome.loadTimes = function() {
            const t = performance.timing || {};
            const base = (t.navigationStart || Date.now()) / 1000;
            return {
                requestTime: base,
                startLoadTime: base,
                commitLoadTime: base,
                finishDocumentLoadTime: (t.domContentLoadedEventEnd || Date.now()) / 1000,
                finishLoadTime: (t.loadEventEnd || Date.now()) / 1000,
                firstPaintTime: agora(),
                firstPaintAfterLoadTime: 0,
                navigationType: "Other",
                wasFetchedViaSpdy: true,
                wasNpnNegotiated: true,
                npnNegotiatedProtocol: "h2",
                wasAlternateProtocolAvailable: false,
                connectionInfo: "h2",
            };
        };
        window.chrome.csi = function() {
            const t = performance.timing || {};
            const inicio = t.navigationStart || Date.now();
            return { startE: inicio, onloadT: t.domContentLoadedEventEnd || Date.now(), pageT: Date.now() - inicio, tran: 15 };
        };
        window.chrome.app = {
            isInstalled: false,
            InstallState: { DISABLED: "disabled", INSTALLED: "installed", NOT_INSTALLED: "not_installed" },
            RunningState: { CANNOT_RUN: "cannot_run", READY_TO_RUN: "ready_to_run", RUNNING: "running" },
            getDetails: function() { return null; },
            getIsInstalled: function() { return false; },
            runningState: function() { return "cannot_run"; },
        };
    } catch(e) {}
})();
""";
