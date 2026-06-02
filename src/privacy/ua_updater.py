import re;
import urllib.request;
from pathlib import Path;

_ROOT = Path(__file__).parent.parent.parent;
_UA_FILE = _ROOT / "data" / "user_agents.txt";

_SOURCES = [
    "https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome",
    "https://www.whatismybrowser.com/guides/the-latest-user-agent/firefox",
    "https://www.whatismybrowser.com/guides/the-latest-user-agent/edge",
    "https://www.whatismybrowser.com/guides/the-latest-user-agent/safari",
    "https://www.whatismybrowser.com/guides/the-latest-user-agent/opera",
];

_MOBILE = ("Android", "iPhone", "iPad", "Mobile");

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
};


def _fetch(url: str) -> list[str]:
    req = urllib.request.Request(url, headers=_HEADERS);
    with urllib.request.urlopen(req, timeout=12) as r:
        html = r.read().decode("utf-8");
    uas = re.findall(r'<span class="code">(Mozilla/5\.0[^<]+)</span>', html);
    return [ua.strip() for ua in uas if not any(m in ua for m in _MOBILE)];


def update(path: Path = _UA_FILE) -> tuple[int, str]:
    collected: list[str] = [];
    errors: list[str] = [];
    for url in _SOURCES:
        browser = url.split("/")[-1];
        try:
            uas = _fetch(url);
            collected.extend(uas);
            print(f"[ua_updater] {browser}: {len(uas)} UAs");
        except Exception as e:
            errors.append(browser);
            print(f"[ua_updater] {browser}: erro — {e}");

    unique = list(dict.fromkeys(collected));
    if not unique:
        return 0, "Nenhum user agent encontrado." + (f" Erros: {', '.join(errors)}" if errors else "");

    path.parent.mkdir(parents=True, exist_ok=True);
    path.write_text("\n".join(unique) + "\n", encoding="utf-8");

    msg = f"{len(unique)} user agents atualizados.";
    if errors:
        msg += f"\nFalha ao buscar: {', '.join(errors)}.";
    return len(unique), msg;


if __name__ == "__main__":
    count, msg = update();
    print(msg);
