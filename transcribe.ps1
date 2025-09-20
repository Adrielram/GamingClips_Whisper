# Script de PowerShell para transcribir videos de gaming
# Uso: .\transcribe.ps1 video.mp4

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$VideoPath
)

# Función para mostrar mensajes con colores
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Verificar que el archivo existe
if (!(Test-Path $VideoPath)) {
    Write-ColorOutput Red "❌ Error: No se encontró el archivo '$VideoPath'"
    exit 1
}

# Obtener nombre del archivo de salida
$VideoFile = Get-Item $VideoPath
$OutputPath = $VideoFile.DirectoryName + "\" + $VideoFile.BaseName + ".srt"

Write-ColorOutput Cyan "🎮 Transcriptor de Gaming - Configuración Optimizada"
Write-Output "=" * 60
Write-Output "📹 Video de entrada: $VideoPath"
Write-Output "📝 Subtítulos de salida: $OutputPath"
Write-Output ""
Write-ColorOutput Yellow "⚙️  Configuración:"
Write-Output "    • Modelo: large-v3 (máxima calidad)"
Write-Output "    • Beam size: 5 (mejor precisión)"
Write-Output "    • Compute type: float16 (velocidad óptima)"
Write-Output "    • Prompt argentino: activado"
Write-Output "    • Device: cuda (GPU si está disponible)"
Write-Output ""

# Activar entorno virtual si existe
if (Test-Path "venv310\Scripts\Activate.ps1") {
    Write-ColorOutput Green "⚡ Activando entorno virtual..."
    & .\venv310\Scripts\Activate.ps1
}

Write-ColorOutput Green "🚀 Iniciando transcripción..."
Write-ColorOutput Yellow "⏳ Esto puede tomar varios minutos dependiendo del video..."
Write-Output ""

try {
    # Ejecutar transcripción
    python transcribe.py $VideoPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Output ""
        Write-ColorOutput Green "✅ ¡Transcripción completada exitosamente!"
        Write-Output "📁 Archivo generado: $OutputPath"
        
        if (Test-Path $OutputPath) {
            $FileSize = (Get-Item $OutputPath).Length
            Write-Output "📊 Tamaño del archivo: $FileSize bytes"
        }
        
        Write-Output ""
        Write-ColorOutput Cyan "🎯 Consejos:"
        Write-Output "    • Revisa el archivo .srt para verificar la calidad"
        Write-Output "    • Si hay errores, usa tools/postprocess_subs.py para limpiar"
        Write-Output "    • Para evaluar calidad: tools/evaluate_wer.py"
    } else {
        throw "Error en la transcripción (código: $LASTEXITCODE)"
    }
    
} catch {
    Write-Output ""
    Write-ColorOutput Red "❌ Error durante la transcripción:"
    Write-ColorOutput Red "    $($_.Exception.Message)"
    Write-Output ""
    Write-ColorOutput Yellow "🔧 Posibles soluciones:"
    Write-Output "    • Verificar que el video no esté corrupto"
    Write-Output "    • Probar con --device cpu si hay problemas de GPU"
    Write-Output "    • Revisar que FFmpeg esté instalado"
    Write-Output "    • Verificar espacio en disco disponible"
    exit 1
}