@echo off
setlocal enabledelayedexpansion

:: ===============================================
:: 🎮 GameClipping - Transcripción Gaming Rápida
:: ===============================================
:: Script para transcripción optimizada gaming
:: Uso: transcribe_gaming.bat archivo_audio.wav
:: ===============================================

if "%~1"=="" (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════╗
    echo ║             🎮 Transcripción Gaming Rápida                      ║
    echo ╚══════════════════════════════════════════════════════════════════╝
    echo.
    echo ❌ Error: Especifica un archivo de audio
    echo.
    echo 💡 Uso: transcribe_gaming.bat archivo_audio.wav
    echo.
    echo 🎯 Ejemplos:
    echo    transcribe_gaming.bat mi_gameplay.wav
    echo    transcribe_gaming.bat "C:\path\to\audio.mp3"
    echo    transcribe_gaming.bat *.wav
    echo.
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║             🎮 Transcripción Gaming Rápida                      ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Verificar si el entorno virtual existe
if not exist "venv\Scripts\python.exe" (
    echo ❌ Error: Entorno virtual no encontrado
    echo.
    echo 💡 Ejecuta primero: install_vad_system.bat
    echo.
    pause
    exit /b 1
)

echo 🔄 Usando entorno VAD Gaming...

:: Verificar archivo de entrada
set "INPUT_FILE=%~1"
if not exist "%INPUT_FILE%" (
    echo ❌ Error: Archivo no encontrado: %INPUT_FILE%
    echo.
    pause
    exit /b 1
)

echo ✅ Archivo de entrada: %INPUT_FILE%

:: Generar nombre de archivo de salida
set "OUTPUT_BASE=%~n1"
set "OUTPUT_DIR=output"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

set "OUTPUT_TXT=%OUTPUT_DIR%\%OUTPUT_BASE%_gaming.txt"
set "OUTPUT_SRT=%OUTPUT_DIR%\%OUTPUT_BASE%_gaming.srt"

echo 📁 Archivos de salida:
echo    TXT: %OUTPUT_TXT%
echo    SRT: %OUTPUT_SRT%
echo.

:: Ejecutar transcripción
echo 🎮 Iniciando transcripción gaming...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

venv\Scripts\python.exe transcribe_vad_advanced.py "%INPUT_FILE%" ^
    --output "%OUTPUT_TXT%" ^
    --profile gaming ^
    --user "gaming_user" ^
    --verbose

set "TRANSCRIBE_RESULT=%errorlevel%"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if %TRANSCRIBE_RESULT% equ 0 (
    echo ✅ Transcripción completada exitosamente!
    echo.
    
    :: Verificar archivos de salida
    if exist "%OUTPUT_TXT%" (
        echo 📄 Archivo TXT creado: %OUTPUT_TXT%
        
        :: Mostrar primeras líneas
        echo.
        echo 👀 Vista previa:
        echo ────────────────────────────────────────
        type "%OUTPUT_TXT%" | more +0
        echo ────────────────────────────────────────
    )
    
    if exist "%OUTPUT_SRT%" (
        echo 📺 Archivo SRT creado: %OUTPUT_SRT%
    )
    
    :: Mostrar estadísticas si existen
    if exist "%OUTPUT_DIR%\%OUTPUT_BASE%_detailed.json" (
        echo 📊 Estadísticas detalladas: %OUTPUT_DIR%\%OUTPUT_BASE%_detailed.json
    )
    
    echo.
    echo 🎉 ¡Transcripción gaming completada!
    
    :: Preguntar si abrir el archivo
    choice /c YN /m "¿Abrir archivo de texto? (Y/N)"
    if !errorlevel!==1 (
        notepad "%OUTPUT_TXT%"
    )
    
) else (
    echo ❌ Error en la transcripción
    echo.
    echo 💡 Posibles soluciones:
    echo    • Verificar que el archivo de audio sea válido
    echo    • Ejecutar: python verify_installation.py
    echo    • Revisar README_VAD_ADVANCED.md para troubleshooting
    echo.
)

echo.
echo 🔚 Proceso terminado
pause