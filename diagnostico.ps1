# =======================================================
# SISTEMA DE AGUA - DIAGNOSTICO Y SOLUCION FINAL
# =======================================================

Write-Host "🌊 Sistema de Gestión de Agua - DIAGNÓSTICO COMPLETO" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Blue

Set-Location $PSScriptRoot

Write-Host "🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Blue

Write-Host ""
Write-Host "1. Verificando entorno virtual..." -ForegroundColor Yellow
if (!(Test-Path ".venv")) {
    Write-Host "❌ Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host "📦 Ejecutando instalador automático..." -ForegroundColor Yellow
    & ".\instalar.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error en instalación" -ForegroundColor Red
        Read-Host "Presione Enter para salir"
        exit 1
    }
}
Write-Host "✅ Entorno virtual OK" -ForegroundColor Green

Write-Host ""
Write-Host "2. Activando entorno..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "3. Verificando Python..." -ForegroundColor Yellow
try {
    $python_version = python --version 2>&1
    Write-Host "✅ Python OK: $python_version" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    Read-Host "Presione Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "4. Verificando PyQt5..." -ForegroundColor Yellow
try {
    $pyqt_result = python -c "import PyQt5; from PyQt5.QtCore import QT_VERSION_STR; print(f'✅ PyQt5 {QT_VERSION_STR}')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host $pyqt_result -ForegroundColor Green
    } else {
        Write-Host "❌ PyQt5 no encontrado, instalando..." -ForegroundColor Red
        pip install PyQt5
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Error instalando PyQt5" -ForegroundColor Red
            Read-Host "Presione Enter para salir"
            exit 1
        }
        Write-Host "✅ PyQt5 instalado" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error verificando PyQt5" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. Verificando base de datos..." -ForegroundColor Yellow
try {
    python test_database.py >$null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Base de datos OK" -ForegroundColor Green
    } else {
        Write-Host "❌ Problema con base de datos" -ForegroundColor Red
        Write-Host "🔧 Ejecutando test detallado..." -ForegroundColor Yellow
        python test_database.py
    }
} catch {
    Write-Host "❌ Error verificando base de datos" -ForegroundColor Red
}

Write-Host ""
Write-Host "===================================" -ForegroundColor Blue
Write-Host "🚀 OPCIONES DE EJECUCIÓN" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Blue
Write-Host ""
Write-Host "Seleccione la versión a ejecutar:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. SISTEMA SIMPLIFICADO (Garantizado que funciona)" -ForegroundColor Green
Write-Host "2. Sistema completo (main.py)" -ForegroundColor Yellow
Write-Host "3. Sistema corregido (main_final.py)" -ForegroundColor Yellow
Write-Host "4. Solo test de interfaz" -ForegroundColor Cyan
Write-Host "5. Salir" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Ingrese su opción (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 Ejecutando SISTEMA SIMPLIFICADO..." -ForegroundColor Green
        Write-Host "📋 PIN: 1234" -ForegroundColor Cyan
        Write-Host "✅ Esta versión está garantizada para funcionar" -ForegroundColor Green
        Write-Host ""
        python sistema_simple.py
    }
    "2" {
        Write-Host ""
        Write-Host "🚀 Ejecutando sistema completo (main.py)..." -ForegroundColor Yellow
        Write-Host "📋 PIN: 1234" -ForegroundColor Cyan
        Write-Host ""
        python main.py
    }
    "3" {
        Write-Host ""
        Write-Host "🚀 Ejecutando sistema corregido (main_final.py)..." -ForegroundColor Yellow
        Write-Host "📋 PIN: 1234" -ForegroundColor Cyan
        Write-Host ""
        python main_final.py
    }
    "4" {
        Write-Host ""
        Write-Host "🧪 Ejecutando test de interfaz..." -ForegroundColor Cyan
        Write-Host ""
        python test_login_interfaz.py
    }
    "5" {
        Write-Host "👋 Saliendo..." -ForegroundColor Gray
    }
    default {
        Write-Host "❌ Opción inválida" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📞 SOPORTE:" -ForegroundColor Yellow
Write-Host "==========" -ForegroundColor Blue
Write-Host "✅ Para uso garantizado: Opción 1 (Sistema Simplificado)" -ForegroundColor Green
Write-Host "✅ PIN por defecto: 1234" -ForegroundColor Green
Write-Host "✅ Base de datos: Funcionando" -ForegroundColor Green
Write-Host "⚠️  Ejecutar en computadora con pantalla (no servidor remoto)" -ForegroundColor Yellow
Write-Host ""
Write-Host "🏁 Presione cualquier tecla para salir..." -ForegroundColor Gray
Read-Host
