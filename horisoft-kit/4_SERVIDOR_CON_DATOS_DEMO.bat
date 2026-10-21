@echo off
chcp 65001 >nul
title Horisoft - 4. Servidor con datos de demostracion
if not exist "%~dp0horisoft-proyecto\manage.py" (
  echo [FALLA] No encuentro la carpeta horisoft-proyecto junto a este archivo.
  pause
  exit /b 1
)
cd /d "%~dp0horisoft-proyecto"

if not exist ".venv\Scripts\activate.bat" (
  echo Primero ejecuta 1_VERIFICAR_ENTORNO.bat
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat

if not exist "%~dp0evidencias" mkdir "%~dp0evidencias"
if errorlevel 1 (
  echo [FALLA] No se pudo crear la carpeta evidencias.
  pause
  exit /b 1
)
set "LOGFILE=%~dp0evidencias\servidor_datos_demo.txt"
set "TEMP_LOG=%TEMP%\horisoft_demo_%RANDOM%_%RANDOM%.txt"
> "%LOGFILE%" echo Horisoft - Servidor con datos de demostracion
if errorlevel 1 (
  echo [FALLA] No se pudo crear el archivo de evidencias.
  pause
  exit /b 1
)
>> "%LOGFILE%" echo Fecha: %date% %time%
>> "%LOGFILE%" echo.

echo ============================================================
echo  PASO 4: servidor web con datos de demostracion
echo ============================================================
echo.
call :ejecutar_registrado "Migraciones" "python manage.py migrate -v 0"
if errorlevel 1 (
  echo [FALLA] La migracion fallo. Revisa evidencias\servidor_datos_demo.txt.
  echo         Esta MySQL encendido en Laragon?
  pause
  exit /b 1
)
call :ejecutar_registrado "Carga de datos de demostracion" "python manage.py crear_datos_demo --paginacion"
if errorlevel 1 (
  echo [FALLA] No se pudieron cargar los datos demo. Revisa evidencias\servidor_datos_demo.txt.
  pause
  exit /b 1
)
echo.
echo ------------------------------------------------------------
echo  Se abrira el navegador en http://127.0.0.1:8000/
echo  Entra con los usuarios de la lista de arriba. Para detener el servidor: Ctrl + C
echo  La salida tambien se guarda en evidencias\servidor_datos_demo.txt.
echo ------------------------------------------------------------
echo.
>> "%LOGFILE%" echo.
>> "%LOGFILE%" echo ===== Inicio del servidor Django (Ctrl+C para detener) =====
start "" http://127.0.0.1:8000/
powershell -NoProfile -Command "& { python -u manage.py runserver 2>&1 | ForEach-Object { $line = $_.ToString(); [Console]::WriteLine($line); [System.IO.File]::AppendAllText('%LOGFILE%', $line + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false)) }; exit $LASTEXITCODE }"
set "SERVER_EXIT=%ERRORLEVEL%"
>> "%LOGFILE%" echo.
>> "%LOGFILE%" echo El servidor se detuvo con codigo %SERVER_EXIT%.
if not "%SERVER_EXIT%"=="0" echo [AVISO] El servidor termino con codigo %SERVER_EXIT%. Revisa evidencias\servidor_datos_demo.txt.
pause
exit /b %SERVER_EXIT%

:ejecutar_registrado
set "STEP_NAME=%~1"
set "STEP_COMMAND=%~2"
echo ===== %STEP_NAME% =====
>> "%LOGFILE%" echo ===== %STEP_NAME% =====
%STEP_COMMAND% > "%TEMP_LOG%" 2>&1
set "STEP_EXIT=%ERRORLEVEL%"
type "%TEMP_LOG%"
type "%TEMP_LOG%" >> "%LOGFILE%"
del "%TEMP_LOG%" >nul 2>&1
if not "%STEP_EXIT%"=="0" (
  >> "%LOGFILE%" echo [FALLA] %STEP_NAME% termino con codigo %STEP_EXIT%.
  exit /b 1
)
>> "%LOGFILE%" echo.
exit /b 0
