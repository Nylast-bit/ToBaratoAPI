# Script para configurar Cloudflare Tunnel para PostgreSQL
# 1. Instalar cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# 2. Autenticar con Cloudflare
cloudflared tunnel login

# 3. Crear tunnel
cloudflared tunnel create tobarato-db

# 4. Configurar tunnel para PostgreSQL (puerto 5432)
# Archivo config.yml:
tunnel: <TUNNEL_ID>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: db.your-domain.com
    service: tcp://localhost:5432
  - service: http_status:404

# 5. Ejecutar tunnel
cloudflared tunnel run tobarato-db
