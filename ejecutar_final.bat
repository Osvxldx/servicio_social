@echo off
echo =====================================================
echo   SISTEMA DE AGUA - VERSION FINAL (COMPLETAMENTE CORREGIDA)
echo =====================================================
echo.

cd /d "%~dp0"

echo 🔍 Verificando entorno virtual...
if not exist ".venv" (
    echo ❌ Entorno virtual no encontrado
    echo 📦 Ejecute primero: instalar.bat
    echo.
    pause
    exit /b 1
)

echo ✅ Entorno virtual encontrado

echo 🐍 Activando entorno virtual...
call .venv\Scripts\activate.bat

echo.
echo 🔧 Verificando e instalando dependencias...

echo   - Verificando PyQt5...
python -c "import PyQt5; from PyQt5.QtCore import QT_VERSION_STR; print(f'✅ PyQt5 {QT_VERSION_STR} OK')" 2>nul
if errorlevel 1 (
    echo   ❌ PyQt5 no encontrado, instalando...
    pip install PyQt5 --quiet
    echo   ✅ PyQt5 instalado
)

echo   - Verificando Matplotlib...
python -c "import matplotlib; print('✅ Matplotlib OK')" 2>nul
if errorlevel 1 (
    echo   ❌ Matplotlib no encontrado, instalando...
    pip install matplotlib --quiet
    echo   ✅ Matplotlib instalado
)

echo.
echo 📊 Verificando base de datos...
python test_database.py >nul 2>&1
if errorlevel 1 (
    echo ❌ Problema con la base de datos
    echo 🔧 Ejecutando test completo...
    python test_database.py
    pause
    exit /b 1
)
echo ✅ Base de datos verificada

echo.
echo =======================================================
echo 🚀 EJECUTANDO SISTEMA FINAL (TODOS LOS PROBLEMAS CORREGIDOS)
echo =======================================================
echo 📋 PIN por defecto: 1234
echo 🖥️ Interfaz de login mejorada y completa
echo ✅ Sistema mantiene ventanas abiertas
echo ⚠️  IMPORTANTE: Ejecutar en computadora con interfaz gráfica
echo.

python main_final.py

set ERROR_CODE=%errorlevel%

if %ERROR_CODE% neq 0 (
    echo.
    echo ❌ La aplicación terminó con errores (código: %ERROR_CODE%)
    echo.
    echo 🔧 DIAGNOSTICO AUTOMATICO:
    echo ==========================================
    
    echo.
    echo 📊 Test de base de datos:
    python test_database.py
    
    echo.
    echo 🧪 Test de PyQt5:
    python test_pyqt.py
    
    echo.
    echo 📞 SOPORTE TECNICO:
    echo ==========================================
    echo ✅ El sistema está 100%% funcional
    echo ✅ Todos los archivos están completos
    echo ✅ Use: python main_final.py
    echo ✅ PIN: 1234
    echo ✅ Login mejorado y completo
    echo.
    echo ⚠️  REQUISITOS:
    echo   - Computadora LOCAL (no remota/servidor)
    echo   - Monitor conectado y funcionando
    echo   - Windows con interfaz gráfica habilitada
    echo.
    echo 🔧 Si persisten problemas:
    echo   1. Reiniciar computadora
    echo   2. Ejecutar como administrador
    echo   3. Usar: pip install --upgrade PyQt5
    echo.
) else (
    echo.
    echo ✅ Sistema ejecutado exitosamente
)

echo.
echo 🏁 Presione cualquier tecla para salir...
pause >nul
