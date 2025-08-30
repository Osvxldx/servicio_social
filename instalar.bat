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

echo [1/4] Python detectado correctamente
echo.

REM Crear entorno virtual
echo [2/4] Creando entorno virtual...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [3/4] Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Instalar dependencias
echo [4/4] Instalando dependencias...
pip install PyQt5 matplotlib
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ===============================================
echo    INSTALACION COMPLETADA EXITOSAMENTE!
echo ===============================================
echo.
echo Para ejecutar la aplicacion:
echo 1. Abra una terminal en esta carpeta
echo 2. Ejecute: .venv\Scripts\activate
echo 3. Ejecute: python main.py
echo.
echo PIN por defecto: 1234
echo.
echo Presione cualquier tecla para ejecutar la aplicacion ahora...
pause >nul

REM Ejecutar la aplicacion
python main.py
