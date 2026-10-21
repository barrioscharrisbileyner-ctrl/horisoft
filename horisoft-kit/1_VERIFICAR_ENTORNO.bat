@echo off
chcp 65001 >nul
title Horisoft - 1. Verificar entorno
if not exist "%~dp0horisoft-proyecto\manage.py" (
  echo [FALLA] No encuentro la carpeta horisoft-proyecto junto a este archivo.
  pause
  exit /b 1
)
cd /d "%~dp0horisoft-proyecto"

echo ============================================================
echo  PASO 1: preparar y verificar el entorno
echo ============================================================
echo.

set "PYTHON="
where py >nul 2>&1
if not errorlevel 1 (
  py -3.13 -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1
  if not errorlevel 1 set "PYTHON=py -3.13"
  if not defined PYTHON (
    py -3.12 -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYTHON=py -3.12"
  )
  if not defined PYTHON (
    py -3.11 -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYTHON=py -3.11"
  )
  if not defined PYTHON (
    py -3.10 -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYTHON=py -3.10"
  )
)
if not defined PYTHON (
  where python >nul 2>&1
  if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1
    if not errorlevel 1 set "PYTHON=python"
  )
)
if not defined PYTHON (
  echo [FALLA] No encontre Python 3.10, 3.11, 3.12 ni 3.13.
  echo         Instala Python 3.13 desde https://www.python.org y marca "Add python.exe to PATH".
  pause
  exit /b 1
)

if not exist ".venv\Scripts\activate.bat" (
  echo Creando el entorno virtual .venv ...
  %PYTHON% -m venv .venv
  if errorlevel 1 (
    echo [FALLA] No se pudo crear el entorno virtual.
    pause
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
python -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1
if errorlevel 1 (
  echo [FALLA] El entorno .venv existente usa una version de Python no compatible.
  echo         Eliminalo y vuelve a ejecutar este archivo con Python 3.10, 3.11, 3.12 o 3.13.
  pause
  exit /b 1
)
echo Instalando dependencias de Python, puede tardar un minuto ...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo [FALLA] No se pudieron instalar las dependencias. Revisa tu conexion a internet.
  pause
  exit /b 1
)
echo.
if not exist "%~dp0herramientas\verificar_entorno.py" (
  echo [FALLA] No encuentro herramientas\verificar_entorno.py.
  pause
  exit /b 1
)
python ..\herramientas\verificar_entorno.py --crear-bd
if errorlevel 1 (
  echo.
  echo [FALLA] La verificacion encontro problemas. Corrigelos antes de continuar.
  pause
  exit /b 1
)
echo.
echo [ OK ] Entorno listo. Continua con 2_PRUEBAS_DJANGO.bat.
pause
