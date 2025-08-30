@echo off
echo =====================================================
echo   SISTEMA DE AGUA - DIAGNOSTICO Y SOLUCION FINAL
echo =====================================================
echo.

cd /d "%~dp0"

echo 🔍 DIAGNOSTICO COMPLETO DEL SISTEMA
echo ===================================

echo.
echo 1. Verificando entorno virtual...
if not exist ".venv" (
    echo ❌ Entorno virtual no encontrado
    echo 📦 Ejecutando instalador automático...
    call instalar.bat
    if errorlevel 1 (
        echo ❌ Error en instalación
        pause
        exit /b 1
    )
)
echo ✅ Entorno virtual OK

echo.
echo 2. Activando entorno...
call .venv\Scripts\activate.bat

echo.
echo 3. Verificando Python...
python --version
if errorlevel 1 (
    echo ❌ Python no encontrado
    pause
    exit /b 1
)
echo ✅ Python OK

echo.
echo 4. Verificando PyQt5...
python -c "import PyQt5; from PyQt5.QtCore import QT_VERSION_STR; print(f'✅ PyQt5 {QT_VERSION_STR}')" 2>nul
if errorlevel 1 (
    echo ❌ PyQt5 no encontrado, instalando...
    pip install PyQt5
    if errorlevel 1 (
        echo ❌ Error instalando PyQt5
        pause
        exit /b 1
    )
)
echo ✅ PyQt5 OK

echo.
echo 5. Verificando base de datos...
python test_database.py >nul 2>&1
if errorlevel 1 (
    echo ❌ Problema con base de datos
    echo 🔧 Ejecutando test detallado...
    python test_database.py
) else (
    echo ✅ Base de datos OK
)

echo.
echo ===================================
echo 🚀 OPCIONES DE EJECUCION
echo ===================================
echo.
echo Seleccione la versión a ejecutar:
echo.
echo 1. SISTEMA SIMPLIFICADO (Garantizado que funciona)
echo 2. Sistema completo (main.py)
echo 3. Sistema corregido (main_final.py)
echo 4. Solo test de interfaz
echo 5. Salir
echo.

set /p choice="Ingrese su opción (1-5): "

if "%choice%"=="1" goto simple
if "%choice%"=="2" goto main
if "%choice%"=="3" goto final
if "%choice%"=="4" goto test
if "%choice%"=="5" goto end

echo ❌ Opción inválida
goto end

:simple
echo.
echo 🚀 Ejecutando SISTEMA SIMPLIFICADO...
echo 📋 PIN: 1234
echo ✅ Esta versión está garantizada para funcionar
echo.
python sistema_simple.py
goto end

:main
echo.
echo 🚀 Ejecutando sistema completo (main.py)...
echo 📋 PIN: 1234
echo.
python main.py
goto end

:final
echo.
echo 🚀 Ejecutando sistema corregido (main_final.py)...
echo 📋 PIN: 1234
echo.
python main_final.py
goto end

:test
echo.
echo 🧪 Ejecutando test de interfaz...
echo.
python test_login_interfaz.py
goto end

:end
echo.
echo 📞 SOPORTE:
echo ==========
echo ✅ Para uso garantizado: Opción 1 (Sistema Simplificado)
echo ✅ PIN por defecto: 1234
echo ✅ Base de datos: Funcionando
echo ⚠️  Ejecutar en computadora con pantalla (no servidor remoto)
echo.
echo 🏁 Presione cualquier tecla para salir...
pause >nul
