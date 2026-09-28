#!/usr/bin/env python3
"""Servicio minimo de registro de consultas del Buscador de Merito (Higüey).
Escucha en 127.0.0.1:8099 (detras de Caddy, ruta /api/*) y registra cada
consulta en consultas.jsonl.  Recibe: GET /api/c?m=<matricula>&f=<0|1>
   f=1  -> matricula encontrada (ficha)
   f=0  -> matricula valida pero no esta en la lista
   f=-1 -> formato invalido
"""
import json
import datetime
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG = "/home/openclaw/.openclaw/workspace/buscador-merito/consultas.jsonl"
BIND = ("127.0.0.1", 8099)


class Handler(BaseHTTPRequestHandler):
    server_version = "merito-logger"

    def _reply(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _handle(self):
        try:
            u = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(u.query)
            mat = (q.get("m", [""])[0] or "")[:40]
            fnd = (q.get("f", [""])[0] or "")[:4]
            if mat:
                rec = {
                    "t": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                    "m": mat,
                    "f": fnd,
                    "ip": (self.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                           or self.client_address[0]),
                    "ua": self.headers.get("User-Agent", "")[:200],
                }
                with open(LOG, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass
        self._reply(204)

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def do_OPTIONS(self):
        self._reply(204)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(BIND, Handler).serve_forever()
