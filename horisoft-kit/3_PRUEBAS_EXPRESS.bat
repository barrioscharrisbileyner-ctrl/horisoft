@echo off
chcp 65001 >nul
title Horisoft - 3. Pruebas de Express
cd /d "%~dp0horisoft-proyecto\backend-node"

where node >nul 2>&1
if errorlevel 1 (
  echo [FALLA] Node.js no esta instalado. Descargalo en https://nodejs.org version LTS.
  pause
  exit /b 1
)

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Se creo el archivo .env a partir de .env.example. No lo muestres en las capturas.
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
set "LOGFILE=%~dp0evidencias\express_pruebas.txt"
set "TEMP_LOG=%TEMP%\horisoft_express_%RANDOM%_%RANDOM%.txt"
set "PRUEBAS_FALLIDAS="
> "%LOGFILE%" echo Horisoft - Pruebas de Express
if errorlevel 1 (
  echo [FALLA] No se pudo crear el archivo de evidencias.
  pause
  exit /b 1
)
>> "%LOGFILE%" echo Fecha: %date% %time%
>> "%LOGFILE%" echo.

echo.
echo ============================================================
echo  PASO 3: pruebas del prototipo Express  - 6 ejecuciones
echo  Despues de cada una se pausa para que puedas capturar.
echo  CAPTURA 2: las 5 suites pruebas-jwt*.js    CAPTURA 3: pruebas-manuales.js
echo  Los resultados tambien se guardan en evidencias\express_pruebas.txt.
echo ============================================================
echo.
echo ===== 1 de 6: pruebas-jwt.js  - esperado: 11 correctas, 0 fallidas =====
call :ejecutar_prueba "pruebas-jwt.js"
if errorlevel 1 set "PRUEBAS_FALLIDAS=1"
echo.
pause

echo ===== 2 de 6: pruebas-jwt-modulos.js  - esperado: 7 correctas, 0 fallidas =====
call :ejecutar_prueba "pruebas-jwt-modulos.js"
if errorlevel 1 set "PRUEBAS_FALLIDAS=1"
echo.
pause

echo ===== 3 de 6: pruebas-jwt-pqr.js  - esperado: 6 correctas, 0 fallidas =====
call :ejecutar_prueba "pruebas-jwt-pqr.js"
if errorlevel 1 set "PRUEBAS_FALLIDAS=1"
echo.
pause

echo ===== 4 de 6: pruebas-jwt-resto.js  - esperado: 29 correctas, 0 fallidas =====
call :ejecutar_prueba "pruebas-jwt-resto.js"
if errorlevel 1 set "PRUEBAS_FALLIDAS=1"
echo.
pause

echo ===== 5 de 6: pruebas-jwt-residencia.js  - esperado: 7 correctas, 0 fallidas =====
call :ejecutar_prueba "pruebas-jwt-residencia.js"
if errorlevel 1 set "PRUEBAS_FALLIDAS=1"
echo.
pause

echo ===== 6 de 6: pruebas-manuales.js  - esperado: 26 con check verde y 7 con X roja =====
echo       los 7 con X son rechazos esperados y estan marcados con la palabra error
call :ejecutar_prueba "pruebas-manuales.js"
if errorlevel 1 set "PRUEBAS_FALLIDAS=1"
echo.
if defined PRUEBAS_FALLIDAS (
  >> "%LOGFILE%" echo.
  >> "%LOGFILE%" echo [FALLA] Una o mas suites terminaron con error.
  echo [FALLA] Una o mas suites terminaron con error.
  echo Revisa evidencias\express_pruebas.txt.
  pause
  exit /b 1
)
>> "%LOGFILE%" echo.
>> "%LOGFILE%" echo [ OK ] Las seis suites finalizaron correctamente.
echo [ OK ] Fin de las pruebas de Express.
echo Resultado guardado en evidencias\express_pruebas.txt
pause
exit /b 0

:ejecutar_prueba
>> "%LOGFILE%" echo ===== %~1 =====
node "%~1" > "%TEMP_LOG%" 2>&1
set "TEST_EXIT=%ERRORLEVEL%"
type "%TEMP_LOG%"
type "%TEMP_LOG%" >> "%LOGFILE%"
del "%TEMP_LOG%" >nul 2>&1
if not "%TEST_EXIT%"=="0" (
  echo [FALLA] %~1 termino con codigo %TEST_EXIT%.
  >> "%LOGFILE%" echo [FALLA] %~1 termino con codigo %TEST_EXIT%.
  exit /b 1
)
exit /b 0
