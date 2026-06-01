import json;
from pathlib import Path;

_SELECTORS_FILE = Path(__file__).parent.parent / "data" / "ad_selectors.txt";


def _load_selectors() -> list[str]:
    if not _SELECTORS_FILE.exists():
        return [];
    selectors = [];
    for line in _SELECTORS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip();
        if line and not line.startswith("#"):
            selectors.append(line);
    return selectors;


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
