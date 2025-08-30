@echo off
echo ===============================================
echo    Sistema de Gestion de Pago de Agua
echo    Script de Instalacion Automatica
echo ===============================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instale Python desde https://python.org/downloads/
    echo Asegurese de marcar "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

echo [1/5] Python detectado correctamente
echo.

REM Crear entorno virtual
echo [2/5] Creando entorno virtual...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [3/5] Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Instalar dependencias
echo [4/5] Instalando dependencias...
pip install PyQt5
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar PyQt5
    pause
    exit /b 1
)

pip install matplotlib
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar matplotlib
    pause
    exit /b 1
)

REM Probar base de datos
echo [5/5] Probando configuracion...
python test_database.py
if %errorlevel% neq 0 (
    echo ERROR: Problemas con la configuracion de la base de datos
    pause
    exit /b 1
)

echo.
echo ===============================================
echo    INSTALACION COMPLETADA EXITOSAMENTE!
echo ===============================================
echo.
echo Para ejecutar la aplicacion:
echo 1. Ejecute: ejecutar.bat
echo 2. O manualmente: .venv\Scripts\activate y python main.py
echo.
echo PIN por defecto: 1234
echo.
echo Presione cualquier tecla para continuar...
pause >nul
