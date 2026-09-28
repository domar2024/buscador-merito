#!/bin/bash
# Asegura (idempotente) la ruta del Buscador de Merito (meritofesd16higuey.online)
# en Caddy: sirve los archivos y proxya /api/* al servicio de registro de consultas.
# Se re-aplica tras reinicios del servidor (ver crontab @reboot).
set -u

# esperar a la API admin de Caddy
for i in $(seq 1 30); do
  if curl -s -m 2 http://127.0.0.1:2019/config/ >/dev/null 2>&1; then break; fi
  sleep 2
done

ROUTES="http://127.0.0.1:2019/config/apps/http/servers/srv0/routes"
if curl -s -m 5 "$ROUTES" 2>/dev/null | grep -q "meritofesd16higuey.online"; then
  echo "ok: ruta meritofesd16higuey.online ya presente"
  exit 0
fi

echo "aplicando ruta del buscador..."
curl -s -m 10 -X POST "$ROUTES" -H "Content-Type: application/json" --data-binary '{"match":[{"host":["meritofesd16higuey.online","www.meritofesd16higuey.online"]}],"handle":[{"handler":"subroute","routes":[{"match":[{"path":["/api/*"]}],"handle":[{"handler":"reverse_proxy","upstreams":[{"dial":"127.0.0.1:8099"}]}]},{"handle":[{"handler":"vars","root":"/home/openclaw/public_html/meritofesd16higuey"},{"handler":"file_server"}]}]}],"terminal":true}'
echo " route-exit=$?"

POL="http://127.0.0.1:2019/config/apps/tls/automation/policies"
if ! curl -s -m 5 "$POL" 2>/dev/null | grep -q "meritofesd16higuey.online"; then
  curl -s -m 10 -X POST "$POL" -H "Content-Type: application/json" --data-binary '{"subjects":["meritofesd16higuey.online","www.meritofesd16higuey.online"],"issuers":[{"module":"acme","ca":"https://acme-v02.api.letsencrypt.org/directory"}]}'
  echo " tls-exit=$?"
fi
echo "listo"
