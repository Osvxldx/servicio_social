@echo off
echo ================================================
echo   SISTEMA DE GESTION DE PAGO DE AGUA - CORREGIDO
echo ================================================
echo.

cd /d "%~dp0"

echo 🔍 Verificando entorno virtual...
if not exist ".venv" (
    echo ❌ Entorno virtual no encontrado
    echo 📦 Ejecute primero: instalar.bat
    pause
    exit /b 1
)

echo ✅ Entorno virtual encontrado

echo 🐍 Activando entorno virtual...
call .venv\Scripts\activate.bat

echo 🔧 Verificando dependencias...
python -c "import PyQt5; print('✅ PyQt5 OK')" 2>nul
if errorlevel 1 (
    echo ❌ PyQt5 no encontrado, instalando...
    pip install PyQt5
)

python -c "import matplotlib; print('✅ Matplotlib OK')" 2>nul
if errorlevel 1 (
    echo ❌ Matplotlib no encontrado, instalando...
    pip install matplotlib
)

echo.
echo 🚀 Ejecutando Sistema de Gestión de Agua (Versión Corregida)...
echo 📋 PIN por defecto: 1234
echo.

python main_corregido.py

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar la aplicación
    echo 🔧 Intentando diagnóstico...
    echo.
    
    echo 📊 Probando base de datos...
    python test_database.py
    
    echo.
    echo 🧪 Probando PyQt5...
    python test_pyqt.py
    
    echo.
    echo 📞 Si el problema persiste:
    echo    1. Verifique que está en una computadora con interfaz gráfica
    echo    2. Ejecute: pip install --upgrade PyQt5
    echo    3. Reinicie la computadora
    echo.
)

echo.
echo 🏁 Presione cualquier tecla para salir...
pause >nul
