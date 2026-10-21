@echo off
chcp 65001 >nul
title Horisoft - 5. Demostraciones de defectos (opcional)
if not exist "%~dp0horisoft-proyecto\backend-node\package.json" (
  echo [FALLA] No encuentro horisoft-proyecto\backend-node.
  pause
  exit /b 1
)
cd /d "%~dp0horisoft-proyecto\backend-node"

where node >nul 2>&1
if errorlevel 1 (
  echo [FALLA] Node.js no esta instalado. Descargalo en https://nodejs.org version LTS.
  pause
  exit /b 1
)

if not exist ".env" (
  if not exist ".env.example" (
    echo [FALLA] No encuentro .env.example para preparar el backend.
    pause
    exit /b 1
  )
  copy ".env.example" ".env" >nul
  if errorlevel 1 (
    echo [FALLA] No se pudo crear .env.
    pause
    exit /b 1
  )
)
if not exist "node_modules" (
  echo Instalando dependencias de Node, puede tardar un minuto ...
  call npm install
  if errorlevel 1 (
    echo [FALLA] No se pudieron instalar las dependencias de Node.
    pause
    exit /b 1
  )
)

if not exist "%~dp0evidencias" mkdir "%~dp0evidencias"
if errorlevel 1 (
  echo [FALLA] No se pudo crear la carpeta evidencias.
  pause
  exit /b 1
)
set "LOGFILE=%~dp0evidencias\demo_defectos.txt"
set "TEMP_LOG=%TEMP%\horisoft_defectos_%RANDOM%_%RANDOM%.txt"
set "DEMO_FALLIDA="
> "%LOGFILE%" echo Horisoft - Demostraciones de defectos
if errorlevel 1 (
  echo [FALLA] No se pudo crear el archivo de evidencias.
  pause
  exit /b 1
)
powershell -NoProfile -Command "[IO.File]::WriteAllText('%LOGFILE%', [IO.File]::ReadAllText('%LOGFILE%'), [Text.UTF8Encoding]::new($true))"
if errorlevel 1 (
  echo [FALLA] No se pudo preparar el archivo de evidencias en UTF-8.
  pause
  exit /b 1
)
>> "%LOGFILE%" echo Fecha: %date% %time%
>> "%LOGFILE%" echo.

if not exist "%~dp0herramientas\demo_inc01_zona_horaria.js" (
  echo [FALLA] No encuentro herramientas\demo_inc01_zona_horaria.js.
  pause
  exit /b 1
)
if not exist "%~dp0herramientas\demo_inc04_inc05_seguridad.js" (
  echo [FALLA] No encuentro herramientas\demo_inc04_inc05_seguridad.js.
  pause
  exit /b 1
)
copy /y "%~dp0herramientas\demo_inc01_zona_horaria.js" . >nul
if errorlevel 1 (
  echo [FALLA] No se pudo preparar la demo de zona horaria.
  pause
  exit /b 1
)
copy /y "%~dp0herramientas\demo_inc04_inc05_seguridad.js" . >nul
if errorlevel 1 (
  del demo_inc01_zona_horaria.js 2>nul
  echo [FALLA] No se pudo preparar la demo de seguridad.
  pause
  exit /b 1
)

echo ============================================================
echo  DEMO 1 - BUG-002 zona horaria (reserva para hoy)
echo  Solo muestra el defecto original cuando en Colombia ya pasaron las 7:00 pm.
echo  En este kit el backend YA esta corregido: debe decir RESERVA ACEPTADA.
echo  La salida se guarda en evidencias\demo_defectos.txt.
echo ============================================================
call :ejecutar_demo "DEMO 1 - BUG-002 zona horaria" "demo_inc01_zona_horaria.js"
if errorlevel 1 set "DEMO_FALLIDA=1"
echo.
pause

echo ============================================================
echo  DEMO 2 - BUG-005 y BUG-006 (siguen ABIERTOS en el prototipo Express)
echo  Se espera ver: HTTP 201 con rol Residente y contrasena en texto plano.
echo ============================================================
call :ejecutar_demo "DEMO 2 - BUG-005 y BUG-006 seguridad" "demo_inc04_inc05_seguridad.js"
if errorlevel 1 set "DEMO_FALLIDA=1"
echo.

del demo_inc01_zona_horaria.js demo_inc04_inc05_seguridad.js 2>nul
if defined DEMO_FALLIDA (
  >> "%LOGFILE%" echo.
  >> "%LOGFILE%" echo [FALLA] Una o mas demos terminaron con error.
  echo [FALLA] Una o mas demos terminaron con error.
  echo Revisa evidencias\demo_defectos.txt.
  pause
  exit /b 1
)
>> "%LOGFILE%" echo.
>> "%LOGFILE%" echo [ OK ] Ambas demos finalizaron correctamente.
echo [ OK ] Resultado guardado en evidencias\demo_defectos.txt
pause
exit /b 0

:ejecutar_demo
set "DEMO_NOMBRE=%~1"
set "DEMO_ARCHIVO=%~2"
echo ===== %DEMO_NOMBRE% =====
>> "%LOGFILE%" echo ===== %DEMO_NOMBRE% =====
node "%DEMO_ARCHIVO%" > "%TEMP_LOG%" 2>&1
set "DEMO_EXIT=%ERRORLEVEL%"
type "%TEMP_LOG%"
type "%TEMP_LOG%" >> "%LOGFILE%"
del "%TEMP_LOG%" >nul 2>&1
if not "%DEMO_EXIT%"=="0" (
  echo [FALLA] %DEMO_ARCHIVO% termino con codigo %DEMO_EXIT%.
  >> "%LOGFILE%" echo [FALLA] %DEMO_ARCHIVO% termino con codigo %DEMO_EXIT%.
  exit /b 1
)
>> "%LOGFILE%" echo.
exit /b 0
