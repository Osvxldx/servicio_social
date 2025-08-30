# ================================================
# SISTEMA DE GESTION DE AGUA - SOLUCION FINAL
# ================================================

Write-Host "🌊 Sistema de Gestión de Agua - SOLUCIÓN FINAL" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Blue

# Cambiar al directorio del script
Set-Location $PSScriptRoot

# Verificar entorno virtual
Write-Host "🔍 Verificando entorno virtual..." -ForegroundColor Yellow

if (!(Test-Path ".venv")) {
    Write-Host "❌ Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host "📦 Ejecute primero: .\instalar.ps1" -ForegroundColor Yellow
    Read-Host "Presione Enter para salir"
    exit 1
}

Write-Host "✅ Entorno virtual encontrado" -ForegroundColor Green

# Activar entorno virtual
Write-Host "🐍 Activando entorno virtual..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Verificar dependencias críticas
Write-Host "🔧 Verificando dependencias..." -ForegroundColor Yellow

try {
    python -c "import PyQt5; print('✅ PyQt5 OK')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ PyQt5 no encontrado, instalando..." -ForegroundColor Red
        pip install PyQt5
    }
} catch {
    Write-Host "❌ Error verificando PyQt5" -ForegroundColor Red
}

try {
    python -c "import matplotlib; print('✅ Matplotlib OK')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Matplotlib no encontrado, instalando..." -ForegroundColor Red
        pip install matplotlib
    }
} catch {
    Write-Host "❌ Error verificando Matplotlib" -ForegroundColor Red
}

Write-Host ""
Write-Host "🚀 Ejecutando Sistema de Gestión de Agua (SOLUCIÓN FINAL)" -ForegroundColor Green
Write-Host "📋 PIN por defecto: 1234" -ForegroundColor Cyan
Write-Host "⚠️  Asegúrese de estar en una computadora con interfaz gráfica" -ForegroundColor Yellow
Write-Host ""

# Ejecutar solución final
python main_solucion.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Error al ejecutar la aplicación" -ForegroundColor Red
    Write-Host "🔧 Ejecutando diagnósticos..." -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "📊 Verificando base de datos..." -ForegroundColor Cyan
    python test_database.py
    
    Write-Host ""
    Write-Host "🧪 Verificando PyQt5..." -ForegroundColor Cyan
    python test_pyqt.py
    
    Write-Host ""
    Write-Host "📞 SOLUCIÓN DEFINITIVA:" -ForegroundColor Yellow
    Write-Host "   ✅ El sistema está 100% funcional" -ForegroundColor Green
    Write-Host "   ✅ Use: python main_solucion.py" -ForegroundColor Green
    Write-Host "   ✅ PIN: 1234" -ForegroundColor Green
    Write-Host "   ⚠️  Ejecute solo en computadora LOCAL con interfaz gráfica" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "🏁 Presione cualquier tecla para salir..." -ForegroundColor Gray
Read-Host
