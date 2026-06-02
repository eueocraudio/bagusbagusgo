import json;
from pathlib import Path;
from ..settings.env_config import get_bool;

PERSONAL_FILE = Path(__file__).parent.parent.parent / "data" / "ad_selectors.txt";
WEB_FILE      = Path(__file__).parent.parent.parent / "data" / "ad_selectors_web.txt";


def _read(path: Path) -> list[str]:
    if not path.exists():
        return [];
    result = [];
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip();
        if line and not line.startswith("#"):
            result.append(line);
    return result;


def _load_selectors() -> list[str]:
    selectors = [];
    if get_bool("AD_SELECTOR_PERSONAL_ENABLED", default=True):
        selectors.extend(_read(PERSONAL_FILE));
    if get_bool("AD_SELECTOR_WEB_ENABLED", default=False):
        selectors.extend(_read(WEB_FILE));
    return list(dict.fromkeys(selectors));


def build_ad_block_js() -> str:
    selectors = _load_selectors();
    selectors_json = json.dumps(selectors, ensure_ascii=False);
    return f"""
(function() {{
    const SELECTORS = {selectors_json};

    function removeAds() {{
        SELECTORS.forEach(function(sel) {{
            try {{
                document.querySelectorAll(sel).forEach(function(el) {{
                    el.remove();
                }});
            }} catch(e) {{}}
        }});
    }}

    removeAds();

    const observer = new MutationObserver(function(mutations) {{
        let dirty = false;
        mutations.forEach(function(m) {{
            if (m.addedNodes.length) dirty = true;
        }});
        if (dirty) removeAds();
    }});

    observer.observe(document.documentElement, {{
        childList: true,
        subtree: true,
    }});
}})();
""";
