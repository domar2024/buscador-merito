#!/usr/bin/env python3
"""Resumen de las consultas registradas en consultas.jsonl (Buscador de Merito)."""
import json
import os
import collections
import datetime

LOG = "/home/openclaw/.openclaw/workspace/buscador-merito/consultas.jsonl"

rows = []
if os.path.exists(LOG):
    with open(LOG, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass

total = len(rows)
found = sum(1 for r in rows if r.get("f") == "1")
notfound = sum(1 for r in rows if r.get("f") == "0")
invalid = sum(1 for r in rows if r.get("f") == "-1")
mats = [r.get("m", "") for r in rows if r.get("m")]
uniq = len(set(mats))
top = collections.Counter(mats).most_common(10)
by_day = collections.Counter((r.get("t", "") or "")[:10] for r in rows)

print(f"Consultas totales : {total}")
print(f"  Encontradas (ficha) : {found}")
print(f"  No encontradas      : {notfound}")
print(f"  Formato invalido    : {invalid}")
print(f"Matriculas unicas consultadas : {uniq}")
print("Por dia:")
for d, c in sorted(by_day.items()):
    print(f"  {d or '(sin fecha)'}: {c}")
print("Top matriculas consultadas:")
for m, c in top:
    print(f"  {m}: {c}")
print("Ultimas 10:")
for r in rows[-10:]:
    print(f"  {r.get('t','')}  {r.get('m','')}  f={r.get('f','')}  {r.get('ip','')}")
