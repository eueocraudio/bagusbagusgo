import urllib.request;
from pathlib import Path;

_WEB_FILE = Path(__file__).parent.parent.parent / "data" / "ad_selectors_web.txt";
_LOCAL_EASYLIST = (
    Path(__file__).parent.parent.parent
    / "data" / "extensions" / "uBlock0.chromium"
    / "assets" / "thirdparties" / "easylist" / "easylist.txt"
);

_EASYLIST_URL = "https://easylist.to/easylist/easylist.txt";

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
};


def _parse_selectors(text: str) -> list[str]:
    selectors = [];
    for line in text.splitlines():
        line = line.strip();
        if not line.startswith("##"):
            continue;
        sel = line[2:].strip();
        if sel and not any(c in sel for c in ("+js(", "#@#", "!#")):
            selectors.append(sel);
    return selectors;


def _fetch_web() -> tuple[list[str], str]:
    req = urllib.request.Request(_EASYLIST_URL, headers=_HEADERS);
    with urllib.request.urlopen(req, timeout=20) as r:
        text = r.read().decode("utf-8", errors="ignore");
    return _parse_selectors(text), "web";


def _fetch_local() -> tuple[list[str], str]:
    if not _LOCAL_EASYLIST.exists():
        return [], "local não encontrado";
    return _parse_selectors(_LOCAL_EASYLIST.read_text(encoding="utf-8", errors="ignore")), "bundled local";


def update(web_file: Path = _WEB_FILE) -> tuple[int, str]:
    selectors, source = [], "";
    try:
        selectors, source = _fetch_web();
        print(f"[ads_updater] EasyList obtida da internet: {len(selectors)} seletores");
    except Exception as e:
        print(f"[ads_updater] falha web ({e}), usando bundled local");
        selectors, source = _fetch_local();
        print(f"[ads_updater] EasyList bundled: {len(selectors)} seletores");

    if not selectors:
        return 0, "Nenhum seletor encontrado.";

    unique = list(dict.fromkeys(selectors));
    web_file.parent.mkdir(parents=True, exist_ok=True);
    web_file.write_text("\n".join(unique) + "\n", encoding="utf-8");
    return len(unique), f"{len(unique)} seletores atualizados (fonte: {source}).";


if __name__ == "__main__":
    count, msg = update();
    print(msg);
