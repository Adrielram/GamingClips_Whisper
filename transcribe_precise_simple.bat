@echo off
REM Transcripción ULTRA-PRECISA - Versión Simple
REM Arrastra tu video aquí para transcripción perfecta

if "%~1"=="" (
    echo 🎯 Arrastra tu video a este archivo para transcripción ULTRA-PRECISA
    pause
    exit /b 1
)

echo 🎯 TRANSCRIPCIÓN ULTRA-PRECISA INICIANDO...
echo Video: %~nx1

cd /d "%~dp0"

if exist "venv310\Scripts\activate.bat" call "venv310\Scripts\activate.bat"

python transcribe_precise.py "%~1"

if errorlevel 1 (
    echo ❌ Error - Intentando método estándar...
    python transcribe.py "%~1"
)

echo ✅ ¡Listo! Busca el archivo .srt en la carpeta de tu video
pause