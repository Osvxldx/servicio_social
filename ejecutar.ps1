# Script PowerShell para ejecutar el Sistema de Gestión de Agua
# Ejecutar con: .\ejecutar.ps1

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "    Sistema de Gestión de Agua" -ForegroundColor Cyan  
Write-Host "    Ejecutando aplicación..." -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si existe el entorno virtual
if (-not (Test-Path ".venv")) {
    Write-Host "ERROR: Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host "Por favor ejecute primero: .\instalar.ps1" -ForegroundColor Yellow
    Read-Host "Presione Enter para continuar"
    exit 1
}

# Cambiar al directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

try {
    Write-Host "[1/3] Activando entorno virtual..." -ForegroundColor Green
    
    # Activar entorno virtual
    & ".\.venv\Scripts\Activate.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo activar el entorno virtual"
    }
    
    Write-Host "[2/3] Verificando dependencias..." -ForegroundColor Green
    
    # Verificar que PyQt5 esté instalado
    & python -c "import PyQt5; print('PyQt5 OK')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: PyQt5 no está instalado correctamente" -ForegroundColor Red
        Write-Host "Ejecute: pip install PyQt5" -ForegroundColor Yellow
        Read-Host "Presione Enter para continuar"
        exit 1
    }
    
    Write-Host "[3/3] Iniciando aplicación..." -ForegroundColor Green
    Write-Host ""
    Write-Host "💧 Sistema de Gestión de Agua iniciando..." -ForegroundColor Cyan
    Write-Host "PIN por defecto: 1234" -ForegroundColor Yellow
    Write-Host ""
    
    # Ejecutar aplicación
    & python main.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ La aplicación terminó con errores" -ForegroundColor Red
        Write-Host ""
        Write-Host "Posibles causas:" -ForegroundColor Yellow
        Write-Host "1. Entorno sin interfaz gráfica (servidor remoto)" -ForegroundColor White
        Write-Host "2. Dependencias no instaladas" -ForegroundColor White
        Write-Host "3. Problemas con el display/GUI" -ForegroundColor White
        Write-Host ""
        Write-Host "Pruebe ejecutar el test sin GUI:" -ForegroundColor Cyan
        Write-Host "python test_database.py" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "✅ Aplicación cerrada correctamente" -ForegroundColor Green
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Presione Enter para continuar"
