#!/usr/bin/env python3
"""
Genera data.js con conteos AGREGADOS de participación (nunca respuestas individuales).

Fuentes:
  1) API de SurveyMonkey (automático, lo usa la GitHub Action):
       SM_TOKEN=...  SM_SURVEY_ID=...  python scripts/actualizar.py
  2) Exportación CSV de SurveyMonkey (manual, en tu compu):
       python scripts/actualizar.py --csv ruta/al/export.csv

Solo lee la fecha de finalización y las preguntas de región y antigüedad.
"""
import argparse, csv, json, os, sys, time, urllib.request, urllib.error
from collections import Counter
from datetime import datetime, timezone, timedelta

ART = timezone(timedelta(hours=-3))
PREG_REGION = "región"          # texto que identifica la pregunta de región
PREG_ANTIG = "antigüedad"       # texto que identifica la pregunta de antigüedad
ORDEN_ANTIG = ["Menos de cinco años", "Cinco años o más"]
SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.js")
API = "https://api.surveymonkey.com/v3"


# ---------- Fuente 1: API de SurveyMonkey ----------
def sm_get(path, token):
    req = urllib.request.Request(API + path, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    for intento in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and intento < 3:
                time.sleep(10 * (intento + 1)); continue
            raise SystemExit(f"SurveyMonkey respondió {e.code}: {e.read()[:300]!r}")


def desde_api(token, survey_id):
    det = sm_get(f"/surveys/{survey_id}/details", token)
    q_reg = q_ant = None
    opciones = {}
    for page in det.get("pages", []):
        for q in page.get("questions", []):
            titulo = " ".join(h.get("heading", "") for h in q.get("headings", [])).lower()
            if q_reg is None and PREG_REGION in titulo: q_reg = q["id"]
            elif q_ant is None and PREG_ANTIG in titulo: q_ant = q["id"]
            for c in (q.get("answers") or {}).get("choices", []):
                opciones[c["id"]] = c.get("text", "").strip()
    if not (q_reg and q_ant):
        raise SystemExit("No encontré las preguntas de región/antigüedad en la encuesta.")

    filas, page = [], 1
    while True:
        r = sm_get(f"/surveys/{survey_id}/responses/bulk?status=completed&per_page=100&page={page}", token)
        for resp in r.get("data", []):
            fin = datetime.fromisoformat(resp["date_modified"]).astimezone(ART)
            reg = ant = None
            for pg in resp.get("pages", []):
                for q in pg.get("questions", []):
                    ids = [a.get("choice_id") for a in q.get("answers", []) if a.get("choice_id")]
                    txt = opciones.get(ids[0]) if ids else None
                    if q["id"] == q_reg: reg = txt
                    elif q["id"] == q_ant: ant = txt
            filas.append((fin, reg, ant))
        if not r.get("links", {}).get("next"): break
        page += 1
    return filas


# ---------- Fuente 2: CSV exportado ----------
def desde_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    head = rows[0]
    def col(clave):
        for i, h in enumerate(head):
            if clave.lower() in h.lower(): return i
        raise SystemExit(f"No encontré la columna que contiene '{clave}'.")
    i_fin, i_reg, i_ant = col("End Date"), col(PREG_REGION), col(PREG_ANTIG)
    filas = []
    for r in rows[1:]:
        if not r or not r[0].strip() or not r[i_fin].strip(): continue
        # El export de SurveyMonkey viene en la zona horaria de la cuenta (Argentina)
        fin = datetime.fromisoformat(r[i_fin]).replace(tzinfo=ART)
        filas.append((fin, r[i_reg].strip() or None, r[i_ant].strip() or None))
    return filas


# ---------- Agregación ----------
def agregar(filas, fuente):
    dias = Counter(f.strftime("%Y-%m-%d") for f, _, _ in filas)
    reg = Counter(r or "Sin dato" for _, r, _ in filas)
    ant = Counter(a or "Sin dato" for _, _, a in filas)
    orden_ant = [k for k in ORDEN_ANTIG if k in ant] + [k for k in ant if k not in ORDEN_ANTIG]
    ultima = max((f for f, _, _ in filas), default=None)
    return {
        "generado": datetime.now(ART).strftime("%Y-%m-%dT%H:%M"),
        "ultimaRespuesta": ultima.strftime("%Y-%m-%dT%H:%M") if ultima else None,
        "fuente": fuente,
        "total": len(filas),
        "porDia": [{"fecha": k, "n": v} for k, v in sorted(dias.items())],
        "region": [{"nombre": k, "n": v} for k, v in sorted(reg.items(), key=lambda x: -x[1])],
        "antiguedad": [{"nombre": k, "n": ant[k]} for k in orden_ant],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="Exportación CSV de SurveyMonkey")
    args = ap.parse_args()
    if args.csv:
        datos = agregar(desde_csv(args.csv), "Exportación de SurveyMonkey")
    else:
        token, sid = os.environ.get("SM_TOKEN"), os.environ.get("SM_SURVEY_ID")
        if not (token and sid):
            sys.exit("Faltan SM_TOKEN y SM_SURVEY_ID (o usá --csv).")
        datos = agregar(desde_api(token, sid), "SurveyMonkey (automático)")

    # Solo reescribe si cambiaron los conteos (evita commits vacíos cada hora)
    previo = None
    if os.path.exists(SALIDA):
        try:
            previo = json.loads(open(SALIDA, encoding="utf-8").read().split("window.TABLERO =", 1)[1].rstrip().rstrip(";"))
        except Exception:
            previo = None
    claves = ("total", "porDia", "region", "antiguedad", "ultimaRespuesta")
    if previo and all(previo.get(k) == datos[k] for k in claves):
        print(f"Sin cambios ({datos['total']} respuestas).")
        return
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("// Generado automáticamente por scripts/actualizar.py — no editar a mano.\n")
        f.write("window.TABLERO = " + json.dumps(datos, ensure_ascii=False, indent=1) + ";\n")
    print(f"data.js actualizado: {datos['total']} respuestas.")


if __name__ == "__main__":
    main()
