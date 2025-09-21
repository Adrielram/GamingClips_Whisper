@echo off
echo ================================================================
echo    🎵 TRANSCRIPTOR CON AUDIO MEJORADO AVANZADO
echo    Pre-procesamiento de audio + Chunking ultra-gradual
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
echo 🎵 Iniciando transcripción con pre-procesamiento de audio avanzado...
echo.
echo 🔄 Pipeline de mejora de audio:
echo    • Reducción de ruido adaptativa
echo    • Mejora de frecuencias de voz
echo    • Compresión dinámica
echo    • Filtros específicos para gaming
echo    • Normalización inteligente
echo.

REM Activar entorno virtual y ejecutar
cd /d "%~dp0"
call venv310\Scripts\activate.bat
python transcribe_enhanced.py "%~1"

REM Verificar si se generó el archivo
set "filename=%~n1"
set "output_dir=%~dp1"
set "srt_file=%output_dir%%filename%_enhanced.srt"

if exist "%srt_file%" (
    echo.
    echo ✅ ¡TRANSCRIPCIÓN CON AUDIO MEJORADO COMPLETADA!
    echo 📄 Archivo generado: %srt_file%
    echo.
    echo 🎵 El audio fue pre-procesado con técnicas avanzadas:
    echo    • Reducción de ruido FFT
    echo    • Ecualización específica para voz
    echo    • Compresión dinámica inteligente
    echo    • Filtros anti-gaming noise
    echo    • Normalización adaptativa
    echo.
    echo 🎯 Subtítulos ultra-graduales (máximo 3 palabras)
    echo    con sincronización perfecta y control de silencios
    echo.
) else (
    echo.
    echo ❌ No se pudo generar el archivo de subtítulos
    echo    Revisa que FFmpeg esté instalado y disponible
    echo.
)

echo Presiona cualquier tecla para continuar...
pause >nul