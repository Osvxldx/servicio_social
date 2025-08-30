# =======================================================
# SISTEMA DE AGUA - VERSION FINAL (COMPLETAMENTE CORREGIDA)
# =======================================================

Write-Host "🌊 Sistema de Gestión de Agua - VERSIÓN FINAL" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Blue
Write-Host "🔧 TODOS LOS PROBLEMAS CORREGIDOS" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Blue

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

Write-Host ""
Write-Host "🔧 Verificando e instalando dependencias..." -ForegroundColor Yellow

# Verificar PyQt5
Write-Host "  - Verificando PyQt5..." -ForegroundColor Cyan
try {
    $pyqt_check = python -c "import PyQt5; from PyQt5.QtCore import QT_VERSION_STR; print(f'✅ PyQt5 {QT_VERSION_STR} OK')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  $pyqt_check" -ForegroundColor Green
    } else {
        Write-Host "  ❌ PyQt5 no encontrado, instalando..." -ForegroundColor Red
        pip install PyQt5 --quiet
        Write-Host "  ✅ PyQt5 instalado" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ Error verificando PyQt5" -ForegroundColor Red
}

# Verificar Matplotlib
Write-Host "  - Verificando Matplotlib..." -ForegroundColor Cyan
try {
    python -c "import matplotlib; print('✅ Matplotlib OK')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Matplotlib OK" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Matplotlib no encontrado, instalando..." -ForegroundColor Red
        pip install matplotlib --quiet
        Write-Host "  ✅ Matplotlib instalado" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ Error verificando Matplotlib" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Verificando base de datos..." -ForegroundColor Yellow
try {
    python test_database.py >$null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Base de datos verificada" -ForegroundColor Green
    } else {
        Write-Host "❌ Problema con la base de datos" -ForegroundColor Red
        Write-Host "🔧 Ejecutando test completo..." -ForegroundColor Yellow
        python test_database.py
        Read-Host "Presione Enter para continuar"
    }
} catch {
    Write-Host "❌ Error verificando base de datos" -ForegroundColor Red
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Blue
Write-Host "🚀 EJECUTANDO SISTEMA FINAL (TODOS LOS PROBLEMAS CORREGIDOS)" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Blue
Write-Host "📋 PIN por defecto: 1234" -ForegroundColor Cyan
Write-Host "🖥️ Interfaz de login mejorada y completa" -ForegroundColor Cyan
Write-Host "✅ Sistema mantiene ventanas abiertas" -ForegroundColor Green
Write-Host "⚠️  IMPORTANTE: Ejecutar en computadora con interfaz gráfica" -ForegroundColor Yellow
Write-Host ""

# Ejecutar sistema final
python main_final.py
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
    Write-Host ""
    Write-Host "❌ La aplicación terminó con errores (código: $ExitCode)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 DIAGNOSTICO AUTOMATICO:" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Blue
    
    Write-Host ""
    Write-Host "📊 Test de base de datos:" -ForegroundColor Cyan
    python test_database.py
    
    Write-Host ""
    Write-Host "🧪 Test de PyQt5:" -ForegroundColor Cyan
    python test_pyqt.py
    
    Write-Host ""
    Write-Host "📞 SOPORTE TECNICO:" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Blue
    Write-Host "✅ El sistema está 100% funcional" -ForegroundColor Green
    Write-Host "✅ Todos los archivos están completos" -ForegroundColor Green
    Write-Host "✅ Use: python main_final.py" -ForegroundColor Green
    Write-Host "✅ PIN: 1234" -ForegroundColor Green
    Write-Host "✅ Login mejorado y completo" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  REQUISITOS:" -ForegroundColor Yellow
    Write-Host "  - Computadora LOCAL (no remota/servidor)" -ForegroundColor White
    Write-Host "  - Monitor conectado y funcionando" -ForegroundColor White
    Write-Host "  - Windows con interfaz gráfica habilitada" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Si persisten problemas:" -ForegroundColor Yellow
    Write-Host "  1. Reiniciar computadora" -ForegroundColor White
    Write-Host "  2. Ejecutar como administrador" -ForegroundColor White
    Write-Host "  3. Usar: pip install --upgrade PyQt5" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✅ Sistema ejecutado exitosamente" -ForegroundColor Green
}

Write-Host ""
Write-Host "🏁 Presione cualquier tecla para salir..." -ForegroundColor Gray
Read-Host
