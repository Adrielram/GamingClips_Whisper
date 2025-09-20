@echo off
setlocal enabledelayedexpansion

echo.
echo 🎯 TRANSCRIPCIÓN ULTRA-PRECISA
echo ==============================
echo 📹 Video: %~nx1
echo 📝 Salida: %~n1.srt
echo.

:: Verificar archivo
if "%~1"=="" (
    echo ❌ Arrastra tu video a este script
    pause
    exit /b 1
)

if not exist "%~1" (
    echo ❌ Archivo no existe
    pause
    exit /b 1
)

echo ✅ Video: %~nx1
echo ✅ Script: transcribe_precise.py  
echo ✅ Método probado y funcionando
echo.

echo 🚀 INICIANDO...
echo.

:: Comando exacto que funciona
cd /d "D:\Ingenieria\GameClipping"
"D:\Ingenieria\GameClipping\venv\Scripts\python.exe" transcribe_precise.py "%~1"

if %errorlevel% equ 0 (
    echo.
    echo ✅ ¡TRANSCRIPCIÓN COMPLETADA!
    echo 📝 Archivo: %~n1.srt
    echo.
) else (
    echo.
    echo ❌ Error
    echo.
)

pause