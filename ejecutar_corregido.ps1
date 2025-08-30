# ================================================
# SISTEMA DE GESTION DE PAGO DE AGUA - CORREGIDO
# ================================================

Write-Host "🌊 Sistema de Gestión de Pago de Agua (Versión Corregida)" -ForegroundColor Cyan
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
Write-Host "🚀 Ejecutando Sistema de Gestión de Agua (Versión Corregida)..." -ForegroundColor Green
Write-Host "📋 PIN por defecto: 1234" -ForegroundColor Cyan
Write-Host ""

# Ejecutar aplicación corregida
python main_corregido.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Error al ejecutar la aplicación" -ForegroundColor Red
    Write-Host "🔧 Ejecutando diagnósticos..." -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "📊 Probando base de datos..." -ForegroundColor Cyan
    python test_database.py
    
    Write-Host ""
    Write-Host "🧪 Probando PyQt5..." -ForegroundColor Cyan
    python test_pyqt.py
    
    Write-Host ""
    Write-Host "📞 Si el problema persiste:" -ForegroundColor Yellow
    Write-Host "   1. Verifique que está en una computadora con interfaz gráfica" -ForegroundColor White
    Write-Host "   2. Ejecute: pip install --upgrade PyQt5" -ForegroundColor White
    Write-Host "   3. Reinicie la computadora" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "🏁 Presione cualquier tecla para salir..." -ForegroundColor Gray
Read-Host
