#!/usr/bin/env python3
"""Resumen diario (hora de RD) de las consultas del Buscador de Merito.
Imprime un mensaje listo para enviar por Telegram."""
import json
import os
import datetime
import collections

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Santo_Domingo")
except Exception:
    TZ = datetime.timezone(datetime.timedelta(hours=-4))

LOG = "/home/openclaw/.openclaw/workspace/buscador-merito/consultas.jsonl"

now = datetime.datetime.now(TZ)
hoy = now.date()

rows = []
if os.path.exists(LOG):
    with open(LOG, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            t = r.get("t", "")
            try:
                dt = datetime.datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(TZ)
            except Exception:
                continue
            if dt.date() == hoy:
                rows.append(r)

total = len(rows)
found = sum(1 for r in rows if r.get("f") == "1")
notfound = sum(1 for r in rows if r.get("f") == "0")
inval = sum(1 for r in rows if r.get("f") == "-1")
mats = [r.get("m", "") for r in rows if r.get("m")]
uniq = len(set(mats))
top = collections.Counter(mats).most_common(5)

fecha = now.strftime("%d/%m/%Y")
if total == 0:
    print(f"📊 Buscador de Mérito — Resumen de hoy ({fecha})\nSin consultas registradas hoy.")
else:
    out = []
    out.append(f"📊 Buscador de Mérito — Resumen de hoy ({fecha})")
    out.append(f"• Consultas totales: {total}")
    out.append(f"• ✅ Encontradas (ficha): {found}")
    out.append(f"• 🌟 No en la lista: {notfound}")
    out.append(f"• ⚠️ Formato inválido: {inval}")
    out.append(f"• 🔎 Matrículas únicas: {uniq}")
    if top:
        out.append("• Top consultadas:")
        for m, c in top:
            out.append(f"   – {m} ({c})")
    print("\n".join(out))
