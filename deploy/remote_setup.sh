#!/bin/bash
# EveryLane Macau — server bootstrap (Alibaba Cloud Linux)
set -eu
APP_DIR=/opt/everylane-macau
SWAPFILE=/swapfile
PY=python3.11

echo "==> swap (1GiB RAM needs headroom)"
if [ ! -f "$SWAPFILE" ]; then
  dd if=/dev/zero of="$SWAPFILE" bs=1M count=1024 status=none
  chmod 600 "$SWAPFILE"
  mkswap "$SWAPFILE"
  swapon "$SWAPFILE"
  grep -q "$SWAPFILE" /etc/fstab || echo "$SWAPFILE none swap sw 0 0" >> /etc/fstab
fi

echo "==> packages"
dnf -y install python3.11 python3.11-pip python3.11-devel nginx git tar which >/dev/null

mkdir -p "$APP_DIR"
cd "$APP_DIR"

echo "==> python venv + deps"
$PY -m venv .venv
. .venv/bin/activate
pip install -U pip setuptools wheel --disable-pip-version-check -q
pip install --disable-pip-version-check -q \
  "fastapi==0.115.6" \
  "uvicorn[standard]==0.34.0" \
  "starlette==0.41.3" \
  "openai==1.59.6" \
  "httpx==0.28.1" \
  "python-dotenv==1.0.1" \
  "pydantic==2.10.4"

echo "==> systemd"
cat >/etc/systemd/system/everylane.service <<'EOF'
[Unit]
Description=EveryLane Macau FastAPI
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/everylane-macau/backend
Environment=PYTHONUTF8=1
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=-/opt/everylane-macau/.env
ExecStart=/opt/everylane-macau/.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000 --workers 1
Restart=always
RestartSec=3
MemoryMax=700M

[Install]
WantedBy=multi-user.target
EOF

echo "==> nginx"
cat >/etc/nginx/conf.d/everylane.conf <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    client_max_body_size 8m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}
EOF
rm -f /etc/nginx/conf.d/default.conf 2>/dev/null || true

if command -v firewall-cmd >/dev/null 2>&1 && systemctl is-active firewalld >/dev/null 2>&1; then
  firewall-cmd --permanent --add-service=http || true
  firewall-cmd --reload || true
fi

systemctl daemon-reload
systemctl enable everylane nginx
systemctl restart everylane
systemctl restart nginx

echo "==> health"
sleep 3
curl -fsS http://127.0.0.1:8000/api/health || true
echo
echo "SETUP_OK"
