import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import asyncio
from playwright.async_api import async_playwright

STATE_PATH = "state.json"
TARGET_URL = "https://www.estrategiaconcursos.com.br/app/dashboard/cursos"
TZ_LOCAL = ZoneInfo("America/Sao_Paulo")
ALERTA_LIMIAR = timedelta(days=3)   # avisa quando faltar <= 3 dias (ajuste como quiser)

def _fmt_delta(td: timedelta) -> str:
    if td.total_seconds() < 0:
        td = -td
        prefixo = "-"
    else:
        prefixo = ""
    dias = td.days
    horas, resto = divmod(td.seconds, 3600)
    minutos, _ = divmod(resto, 60)
    partes = []
    if dias: partes.append(f"{dias}d")
    if horas: partes.append(f"{horas}h")
    if minutos or not partes: partes.append(f"{minutos}m")
    return prefixo + " ".join(partes)

def carregar_state(path: str | Path) -> dict:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    # normaliza: garante que cookies usem "expires" quando houver "expirationDate"
    for c in raw.get("cookies", []):
        if "expires" not in c and "expirationDate" in c:
            try:
                c["expires"] = int(float(c["expirationDate"]))
            except Exception:
                pass
    return raw

def relatorio_expiracao(state: dict) -> list[dict]:
    agora_utc = datetime.now(timezone.utc)
    linhas = []
    for c in state.get("cookies", []):
        nome = c.get("name", "")
        dominio = c.get("domain", "")
        path = c.get("path", "/")
        expires = c.get("expires")
        # considera "0" ou None como sessão
        if not expires:
            linhas.append({
                "name": nome,
                "domain": dominio,
                "path": path,
                "expira_em": "sessão",
                "expira_quando": "sessão",
                "restante_segundos": float("inf"),
                "alerta": ""
            })
            continue

        try:
            exp_utc = datetime.fromtimestamp(int(float(expires)), tz=timezone.utc)
        except Exception:
            linhas.append({
                "name": nome,
                "domain": dominio,
                "path": path,
                "expira_em": "desconhecido",
                "expira_quando": "inválido",
                "restante_segundos": float("inf"),
                "alerta": "⚠️ timestamp inválido"
            })
            continue

        restante = exp_utc - agora_utc
        exp_local = exp_utc.astimezone(TZ_LOCAL)
        alerta = "⚠️ expira em breve" if restante <= ALERTA_LIMIAR else ""
        linhas.append({
            "name": nome,
            "domain": dominio,
            "path": path,
            "expira_em": _fmt_delta(restante),
            "expira_quando": exp_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "restante_segundos": restante.total_seconds(),
            "alerta": alerta
        })

    # ordena: primeiro os que têm data (mais próximos), depois sessão
    linhas.sort(key=lambda r: (r["restante_segundos"]))
    return linhas

def imprimir_relatorio(linhas: list[dict]) -> None:
    # cabeçalho compacto
    print(f"{'Cookie':35} {'Domínio':32} {'Falta':10} {'Expira em':25} {'Alerta'}")
    print("-"*120)
    for r in linhas:
        nome = (r["name"][:33] + "…") if len(r["name"]) > 34 else r["name"]
        dom = (r["domain"][:30] + "…") if len(r["domain"]) > 31 else r["domain"]
        print(f"{nome:35} {dom:32} {r['expira_em']:10} {r['expira_quando']:25} {r['alerta']}")

async def abrir_com_state(state: dict):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=state)
        page = await context.new_page()
        await page.goto(TARGET_URL)
        # espere um pouco para ver a sessão
        await page.wait_for_timeout(3000)
        # opcional: persista de novo, caso queira atualizar state
        # await context.storage_state(path="state.refrescado.json")

if __name__ == "__main__":
    state = carregar_state(STATE_PATH)
    linhas = relatorio_expiracao(state)
    imprimir_relatorio(linhas)

    # Descomente se quiser já abrir o navegador usando o mesmo state:
    # asyncio.run(abrir_com_state(state))
