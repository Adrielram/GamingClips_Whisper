@echo off
echo ================================================================
echo    🎯 TRANSCRIPTOR MULTIPASS ADAPTATIVO
echo    Múltiples pasadas + Merge inteligente + Ultra-precisión
echo ================================================================
echo.

REM Verificar si se pasó un archivo
if "%~1"=="" (
    echo ❌ Por favor, arrastra un archivo de video a este .bat
    echo.
    pause
    exit /b 1
)

REM Verificar si el archivo existe
if not exist "%~1" (
    echo ❌ El archivo no existe: %~1
    echo.
    pause
    exit /b 1
)

echo 📹 Archivo: %~1
echo 🎯 Iniciando transcripción multipass adaptativa...
echo.
echo 🔄 Estrategia de múltiples pasadas:
echo    • Pasada 1: CONSERVADORA (alta confianza, speech claro)
echo    • Pasada 2: AGRESIVA (cubre tiempos muertos)
echo    • Pasada 3: ULTRA-AGRESIVA (detecta susurros)
echo    • Merge inteligente priorizando por confianza
echo    • Relleno de gaps con segmentos de menor confianza
echo.

REM Activar entorno virtual y ejecutar
cd /d "%~dp0"
call venv310\Scripts\activate.bat
python transcribe_multipass.py "%~1"

REM Verificar si se generó el archivo
set "filename=%~n1"
set "output_dir=%~dp1"
set "srt_file=%output_dir%%filename%_multipass.srt"

if exist "%srt_file%" (
    echo.
    echo ✅ ¡TRANSCRIPCIÓN MULTIPASS COMPLETADA!
    echo 📄 Archivo generado: %srt_file%
    echo.
    echo 🎯 Estrategias aplicadas exitosamente:
    echo    • 3 pasadas con diferentes niveles de agresividad
    echo    • Merge inteligente eliminando duplicados
    echo    • Priorización por confianza y consistencia
    echo    • Relleno de gaps para máxima cobertura
    echo    • Chunking ultra-gradual (máximo 3 palabras)
    echo.
    echo 📊 Esta es la transcripción más completa posible
    echo    cubriendo desde speech claro hasta susurros
    echo.
) else (
    echo.
    echo ❌ No se pudo generar el archivo de subtítulos
    echo    Revisa que el modelo Whisper esté disponible
    echo.
)

echo Presiona cualquier tecla para continuar...
pause >nul