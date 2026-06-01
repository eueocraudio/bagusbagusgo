import random;
from pathlib import Path;

_UA_FILE = Path(__file__).parent.parent / "data" / "user_agents.txt";


def random_user_agent() -> str:
    if not _UA_FILE.exists():
        _UA_FILE.parent.mkdir(parents=True, exist_ok=True);
        _UA_FILE.write_text("");
        return "";
    agents = [line.strip() for line in _UA_FILE.read_text().splitlines() if line.strip()];
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

    return f"""
(function() {{
    const ua = {ua!r};
    Object.defineProperty(navigator, 'userAgent',   {{ get: () => ua }});
    Object.defineProperty(navigator, 'appVersion',  {{ get: () => ua.replace('Mozilla/', '') }});
    Object.defineProperty(navigator, 'vendor',      {{ get: () => {vendor!r} }});
    Object.defineProperty(navigator, 'platform',    {{ get: () => {platform!r} }});
    Object.defineProperty(navigator, 'webdriver',   {{ get: () => undefined }});
    Object.defineProperty(navigator, 'languages',   {{ get: () => ['pt-BR', 'pt', 'en-US', 'en'] }});
    delete window.navigator.__proto__.webdriver;
}})();
""";
