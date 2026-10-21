@echo off
chcp 65001 >nul
title Horisoft - 2. Pruebas de Django
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
set "LOGFILE=%~dp0evidencias\django_pruebas.txt"
set "TEMP_LOG=%TEMP%\horisoft_django_%RANDOM%_%RANDOM%.txt"

> "%LOGFILE%" echo Horisoft - Migraciones y pruebas de Django
if errorlevel 1 (
  echo [FALLA] No se pudo crear el archivo de evidencias.
  pause
  exit /b 1
)

echo ============================================================
echo  PASO 2: migraciones y pruebas automaticas de Django
echo ============================================================
echo.
echo ===== Migraciones =====
>> "%LOGFILE%" echo.
>> "%LOGFILE%" echo ===== Migraciones =====
python manage.py migrate > "%TEMP_LOG%" 2>&1
set "COMMAND_EXIT=%ERRORLEVEL%"
type "%TEMP_LOG%"
type "%TEMP_LOG%" >> "%LOGFILE%"
del "%TEMP_LOG%" >nul 2>&1
if not "%COMMAND_EXIT%"=="0" (
  echo.
  echo [FALLA] La migracion fallo. Revisa el mensaje de arriba y evidencias\django_pruebas.txt.
  echo         Si dice error 2003, MySQL no esta encendido: abre Laragon y presiona Start All.
  pause
  exit /b 1
)
echo.
echo ------------------------------------------------------------
echo  Ejecutando las pruebas. Al final debe decir: Ran 40 tests ... OK
echo  Cuando termine, TOMA LA CAPTURA 1 (Figura 1).
echo ------------------------------------------------------------
echo.
>> "%LOGFILE%" echo.
>> "%LOGFILE%" echo ===== Pruebas Django =====
python manage.py test -v 2 > "%TEMP_LOG%" 2>&1
set "COMMAND_EXIT=%ERRORLEVEL%"
type "%TEMP_LOG%"
type "%TEMP_LOG%" >> "%LOGFILE%"
del "%TEMP_LOG%" >nul 2>&1
if not "%COMMAND_EXIT%"=="0" (
  echo.
  echo [FALLA] Las pruebas de Django fallaron. Revisa evidencias\django_pruebas.txt.
  pause
  exit /b 1
)
echo.
echo [ OK ] Resultado guardado en evidencias\django_pruebas.txt
pause
