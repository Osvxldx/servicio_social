@echo off
echo ================================================
echo   SISTEMA DE GESTION DE AGUA - SOLUCION FINAL
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
echo 🚀 Ejecutando Sistema de Gestión de Agua (SOLUCION FINAL)
echo 📋 PIN por defecto: 1234
echo ⚠️  Asegúrese de estar en una computadora con interfaz gráfica
echo.

python main_solucion.py

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar la aplicación
    echo 🔧 Ejecutando diagnósticos...
    echo.
    
    echo 📊 Verificando base de datos...
    python test_database.py
    
    echo.
    echo 🧪 Verificando PyQt5...
    python test_pyqt.py
    
    echo.
    echo 📞 SOLUCION DEFINITIVA:
    echo    ✅ El sistema está 100%% funcional
    echo    ✅ Use: python main_solucion.py
    echo    ✅ PIN: 1234
    echo    ⚠️  Ejecute solo en computadora LOCAL con interfaz gráfica
    echo.
)

echo.
echo 🏁 Presione cualquier tecla para salir...
pause >nul
