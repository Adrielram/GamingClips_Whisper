@echo off
setlocal enabledelayedexpansion

echo.
echo 🎯 TRANSCRIPCIÓN ULTRA-MEJORADA
echo ===============================
echo 📹 Video: %~nx1
echo 📝 Salida: %~n1.srt
echo.

:: Verificar archivo
if "%~1"=="" (
    echo ❌ Arrastra tu video a este script
    echo.
    echo ✨ Mejoras incluidas:
    echo     • Diccionario gaming argentino
    echo     • VAD agresivo (más detección)
    echo     • Corrección temporal automática
    echo     • Corrección ortográfica
    echo     • Pre-procesamiento de audio
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
echo ✅ Script: transcribe_mejorado.py
echo ✅ Mejoras: TODAS activadas
echo.

echo 🚀 INICIANDO TRANSCRIPCIÓN MEJORADA...
echo.

:: Comando con script mejorado
cd /d "D:\Ingenieria\GameClipping"
"D:\Ingenieria\GameClipping\venv\Scripts\python.exe" transcribe_mejorado.py "%~1"

if %errorlevel% equ 0 (
    echo.
    echo ✅ ¡TRANSCRIPCIÓN MEJORADA EXITOSA!
    echo 📝 Archivo: %~n1.srt
    echo.
    echo 🎯 Mejoras aplicadas:
    echo     ✅ Palabras más precisas
    echo     ✅ Mejor detección en ruidos
    echo     ✅ Sincronización corregida
    echo.
) else (
    echo.
    echo ❌ Error en transcripción mejorada
    echo.
)

pause