#!/usr/bin/env bash
# 街知巷聞 · EveryLane Macau — macOS / Linux launcher
set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  街知巷聞 · EveryLane Macau — 澳門深度遊 AI 智能體"
echo "============================================================"
echo "[1/2] 安裝相依套件..."
python3 -m pip install -r requirements.txt

echo "[2/2] 啟動伺服器：http://127.0.0.1:8000"
( sleep 2 && { command -v open >/dev/null && open http://127.0.0.1:8000 || xdg-open http://127.0.0.1:8000 ; } ) >/dev/null 2>&1 &

cd backend
exec python3 -m uvicorn app:app --host 127.0.0.1 --port 8000
