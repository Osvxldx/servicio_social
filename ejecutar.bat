@echo off
title Sistema de Gestion de Agua

REM Verificar si existe el entorno virtual
if not exist ".venv\" (
    echo ERROR: Entorno virtual no encontrado
    echo Por favor ejecute primero instalar.bat
    pause
    exit /b 1
)

REM Activar entorno virtual y ejecutar aplicacion
echo Iniciando Sistema de Gestion de Agua...
call .venv\Scripts\activate.bat && python main.py

REM Si hay error, mostrar mensaje
if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo ejecutar la aplicacion
    echo Verifique que la instalacion se haya completado correctamente
    pause
)
