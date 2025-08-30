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
echo.

REM Cambiar al directorio correcto
cd /d "%~dp0"

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Verificar que se activo correctamente
if %errorlevel% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

REM Ejecutar aplicacion
python main.py

REM Si hay error, mostrar mensaje
if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo ejecutar la aplicacion
    echo Posibles causas:
    echo 1. Ejecutar en un entorno sin interfaz grafica ^(servidor remoto^)
    echo 2. Dependencias no instaladas correctamente
    echo 3. Problemas con PyQt5
    echo.
    echo Pruebe ejecutar: python test_database.py
    echo Para verificar que el backend funciona
    pause
)
