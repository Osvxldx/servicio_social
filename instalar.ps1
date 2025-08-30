# Script PowerShell para instalar el Sistema de Gestión de Agua
# Ejecutar con: .\instalar.ps1

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "    Sistema de Gestión de Agua" -ForegroundColor Cyan
Write-Host "    Instalación Automática" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python está instalado
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "[✓] Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor instale Python desde https://python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Asegúrese de marcar 'Add Python to PATH' durante la instalación" -ForegroundColor Yellow
    Read-Host "Presione Enter para continuar"
    exit 1
}

# Cambiar al directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

try {
    Write-Host ""
    Write-Host "[1/5] Creando entorno virtual..." -ForegroundColor Green
    
    # Crear entorno virtual
    & python -m venv .venv
    
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo crear el entorno virtual"
    }
    
    Write-Host "[2/5] Activando entorno virtual..." -ForegroundColor Green
    
    # Activar entorno virtual
    & ".\.venv\Scripts\Activate.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo activar el entorno virtual"
    }
    
    Write-Host "[3/5] Instalando PyQt5..." -ForegroundColor Green
    
    # Instalar PyQt5
    & pip install PyQt5
    
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo instalar PyQt5"
    }
    
    Write-Host "[4/5] Instalando matplotlib..." -ForegroundColor Green
    
    # Instalar matplotlib
    & pip install matplotlib
    
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo instalar matplotlib"
    }
    
    Write-Host "[5/5] Probando configuración..." -ForegroundColor Green
    
    # Probar base de datos
    & python test_database.py
    
    if ($LASTEXITCODE -ne 0) {
        throw "Problemas con la configuración de la base de datos"
    }
    
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "    ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para ejecutar la aplicación:" -ForegroundColor Cyan
    Write-Host "1. Ejecute: .\ejecutar.ps1" -ForegroundColor White
    Write-Host "2. O manualmente: .\ejecutar.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "PIN por defecto: 1234" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Presione Enter para continuar"
