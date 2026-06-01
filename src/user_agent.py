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
