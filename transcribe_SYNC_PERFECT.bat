@echo off
setlocal enabledelayedexpansion

echo.
echo 🎯 TRANSCRIPCIÓN SYNC-PERFECT
echo =============================
echo 📹 Video: %~nx1
echo 📝 Salida: %~n1.srt
echo.

:: Verificar archivo
if "%~1"=="" (
    echo ❌ Arrastra tu video a este script
    echo.
    echo ✨ Características SYNC-PERFECT:
    echo     • Timestamps originales de Whisper
    echo     • Sin corrección temporal (que causa drift)
    echo     • Configuración conservadora de VAD
    echo     • Agrupación inteligente sin modificar timing
    echo.
    pause
    exit /b 1
)

if not exist "%~1" (
    echo ❌ Archivo no existe
    pause
    exit /b 1
)

echo ✅ Video: %~nx1
echo ✅ Script: transcribe_sync_perfect.py
echo ✅ Modo: SYNC-PERFECT (sin modificar timestamps)
echo.

echo 🚀 INICIANDO TRANSCRIPCIÓN SYNC-PERFECT...
echo.

:: Comando con script sync-perfect
cd /d "D:\Ingenieria\GameClipping"
"D:\Ingenieria\GameClipping\venv\Scripts\python.exe" transcribe_sync_perfect.py "%~1"

if %errorlevel% equ 0 (
    echo.
    echo ✅ ¡TRANSCRIPCIÓN SYNC-PERFECT EXITOSA!
    echo 📝 Archivo: %~n1.srt
    echo.
    echo 🎯 Optimizaciones aplicadas:
    echo     ✅ Sincronización perfecta mantenida
    echo     ✅ Palabras corregidas sin afectar timing
    echo     ✅ Agrupación inteligente
    echo.
) else (
    echo.
    echo ❌ Error en transcripción sync-perfect
    echo.
)

pause