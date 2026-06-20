@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   街知巷聞 · EveryLane Macau  —  澳門深度遊 AI 智能體
echo ============================================================
echo.
echo [1/2] 安裝相依套件 (首次執行需要少許時間)...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo 安裝失敗，請確認已安裝 Python 3.10+ 並已加入 PATH。
  pause
  exit /b 1
)
echo.
echo [2/2] 啟動伺服器：http://127.0.0.1:8000
echo       （未設定 DASHSCOPE_API_KEY 時會以離線示範引擎完整運行）
echo       按 Ctrl+C 可停止伺服器。
echo.
start "" http://127.0.0.1:8000
cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8000
pause
