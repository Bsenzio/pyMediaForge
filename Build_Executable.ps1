$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
function Check-Exit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "Error en: $Step (codigo $LASTEXITCODE)" }
}
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
    Check-Exit 'Crear entorno virtual'
}
$PythonExe = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $PythonExe -m pip install --upgrade pip
Check-Exit 'Actualizar pip'
& $PythonExe -m pip install -r requirements-dev.txt
Check-Exit 'Instalar dependencias'
& $PythonExe -m unittest discover -s tests -v
Check-Exit 'Pruebas'
& $PythonExe -m PyInstaller --noconfirm --clean --onefile --windowed --name MediaForge --collect-all imageio_ffmpeg app.py
Check-Exit 'Compilar ejecutable'
Write-Host 'Listo: dist\MediaForge.exe' -ForegroundColor Green
