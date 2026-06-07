@echo off
setlocal

set ROOT=%~dp0
set BACKEND_DIR=%ROOT%backend
set FRONTEND_DIR=%ROOT%frontend

if not exist "%BACKEND_DIR%\.venv" (
  echo Creating backend virtual environment...
  python -m venv "%BACKEND_DIR%\.venv"
)

call "%BACKEND_DIR%\.venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r "%BACKEND_DIR%\requirements.txt"

if not exist "%FRONTEND_DIR%\node_modules" (
  pushd "%FRONTEND_DIR%"
  npm install
  popd
)

start "Healio Backend" cmd /k "cd /d %BACKEND_DIR% && .venv\Scripts\activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
start "Healio Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

echo Healio is starting.
echo Backend:  http://127.0.0.1:8000/api/health
echo Frontend: http://127.0.0.1:5173

