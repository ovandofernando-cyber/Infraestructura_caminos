#!/bin/bash
# uso: infra_s3get.sh <dir_destino> <nombre_archivo> <url_presignada>
d="$1"; n="$2"; u="$3"; mkdir -p "$d"
curl -sS -m 300 -o "$d/$n.part" -w "%{http_code} %{size_download}\n" "$u" > /tmp/claude-0/s3code 2>&1
c=$(cut -d' ' -f1 /tmp/claude-0/s3code); cat /tmp/claude-0/s3code
if [ "$c" = "200" ]; then mv "$d/$n.part" "$d/$n"; else rm -f "$d/$n.part"; fi
