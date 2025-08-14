import json
from pathlib import Path

SAMESITE_MAP = {
    None: None,
    "": None,
    "unspecified": None,          # remove
    "no_restriction": "None",
    "no_restrictions": "None",
    "none": "None",
    "lax": "Lax",
    "strict": "Strict",
}

def load_and_sanitize_state(path: str | Path) -> dict:
    """Load a Playwright storage state JSON and sanitize cookies for Playwright."""
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))
    cookies = raw.get("cookies", [])
    fixed = []
    for c in cookies:
        c = c.copy()
        # normalize sameSite
        ss = c.get("sameSite")
        key = ss.strip().lower() if isinstance(ss, str) else ss
        mapped = SAMESITE_MAP.get(key, None)
        if mapped is None:
            c.pop("sameSite", None)
        else:
            c["sameSite"] = mapped

        # ensure expires exists if expirationDate provided
        if "expires" not in c and "expirationDate" in c:
            try:
                c["expires"] = int(float(c["expirationDate"]))
            except Exception:
                pass
            c.pop("expirationDate", None)

        # normalize expires type
        if "expires" in c and c["expires"]:
            try:
                c["expires"] = int(float(c["expires"]))
            except Exception:
                c.pop("expires", None)

        # hostOnly ajusta domínio (sem ponto inicial)
        dom = c.get("domain")
        if c.get("hostOnly") and isinstance(dom, str) and dom.startswith("."):
            c["domain"] = dom.lstrip(".")

        fixed.append(c)
    raw["cookies"] = fixed
    return raw
