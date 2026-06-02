import json;
from pathlib import Path;
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile;

_FILENAME = "websettings.json";

_DEFAULTS: dict[str, bool] = {
    "AutoLoadImages":                   True,
    "JavascriptEnabled":                True,
    "JavascriptCanOpenWindows":         False,
    "JavascriptCanAccessClipboard":     False,
    "JavascriptCanPaste":               False,
    "LocalStorageEnabled":              True,
    "LocalContentCanAccessRemoteUrls":  False,
    "LocalContentCanAccessFileUrls":    True,
    "XSSAuditingEnabled":               False,
    "SpatialNavigationEnabled":         False,
    "LinksIncludedInFocusChain":        True,
    "HyperlinkAuditingEnabled":         False,
    "ScrollAnimatorEnabled":            False,
    "ErrorPageEnabled":                 True,
    "PluginsEnabled":                   False,
    "FullScreenSupportEnabled":         True,
    "ScreenCaptureEnabled":             False,
    "WebGLEnabled":                     True,
    "Accelerated2dCanvasEnabled":       True,
    "AutoLoadIconsForPage":             True,
    "TouchIconsEnabled":                False,
    "FocusOnNavigationEnabled":         True,
    "PrintElementBackgrounds":          True,
    "AllowRunningInsecureContent":      False,
    "AllowGeolocationOnInsecureOrigins":False,
    "AllowWindowActivationFromJavaScript":False,
    "ShowScrollBars":                   True,
    "PlaybackRequiresUserGesture":      False,
    "WebRTCPublicInterfacesOnly":       False,
    "DnsPrefetchEnabled":               False,
    "PdfViewerEnabled":                 True,
    "NavigateOnDropEnabled":            True,
    "ForceDarkMode":                    True,
    "BackForwardCacheEnabled":          True,
    "ReadingFromCanvasEnabled":         True,
    "TouchEventsApiEnabled":            False,
    "TrimAccessibilityIdentifiers":     False,
    "PreferCSSMarginsForPrinting":      False,
    "PrintHeaderAndFooter":             False,
};


def _attr(name: str) -> QWebEngineSettings.WebAttribute:
    return QWebEngineSettings.WebAttribute[name];


def load(base_dir: Path) -> dict[str, bool]:
    path = Path(base_dir) / _FILENAME;
    if not path.exists():
        return dict(_DEFAULTS);
    try:
        data = json.loads(path.read_text(encoding="utf-8"));
        result = dict(_DEFAULTS);
        result.update({k: bool(v) for k, v in data.items() if k in _DEFAULTS});
        return result;
    except Exception:
        return dict(_DEFAULTS);


def save(base_dir: Path, settings: dict[str, bool]):
    path = Path(base_dir) / _FILENAME;
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8");


def apply(profile: QWebEngineProfile, settings: dict[str, bool]):
    s = profile.settings();
    for name, value in settings.items():
        try:
            s.setAttribute(_attr(name), value);
        except Exception as e:
            print(f"[websettings] aviso: {name} — {e}");
