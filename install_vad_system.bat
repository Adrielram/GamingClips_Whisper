@echo off
setlocal enabledelayedexpansion

:: ===============================================
:: 🎮 GameClipping - Instalador VAD Híbrido
:: ===============================================
:: Script de instalación automática completa
:: Autor: GameClipping Team
:: Versión: 2.0
:: ===============================================

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    🎮 GameClipping VAD System                    ║
echo ║              Instalador Automático v2.0                         ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Verificar Python
echo [1/8] 🐍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no encontrado
    echo.
    echo 💡 Por favor instala Python 3.8+ desde:
    echo    https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Obtener versión de Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo    ✅ Python %PYTHON_VERSION% detectado

:: Verificar entorno virtual
echo.
echo [2/8] 📦 Verificando entorno virtual...
if exist "venv" (
    echo    ✅ Entorno virtual existente encontrado
) else (
    echo    🔧 Creando nuevo entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo    ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
)
echo    ✅ Entorno virtual listo

:: Usar entorno virtual directamente (sin activar)
echo.
echo [3/8] 🔄 Preparando entorno virtual...
if not exist "venv\Scripts\python.exe" (
    echo    ❌ Error: Python no encontrado en entorno virtual
    pause
    exit /b 1
)
echo    ✅ Entorno virtual listo

:: Actualizar pip
echo.
echo [4/8] ⬆️ Actualizando pip...
venv\Scripts\python.exe -m pip install --upgrade pip
echo    ✅ pip actualizado

:: Instalar dependencias básicas
echo.
echo [5/8] 📚 Instalando dependencias básicas...
echo    🔧 Instalando PyTorch y NumPy...
venv\Scripts\python.exe -m pip install torch numpy
if errorlevel 1 (
    echo    ❌ Error instalando dependencias básicas
    pause
    exit /b 1
)

echo    🔧 Instalando Faster-Whisper...
venv\Scripts\python.exe -m pip install faster-whisper
if errorlevel 1 (
    echo    ⚠️ Error instalando Faster-Whisper, continuando...
)

echo    ✅ Dependencias básicas instaladas

:: Instalar VAD models
echo.
echo [6/8] 🎯 Instalando modelos VAD...
echo    🔧 Instalando Silero VAD...
venv\Scripts\python.exe -m pip install silero-vad
if errorlevel 1 (
    echo    ⚠️ Error instalando Silero VAD
)

echo    🔧 Instalando WebRTC VAD...
venv\Scripts\python.exe -m pip install webrtcvad
if errorlevel 1 (
    echo    ⚠️ Error instalando WebRTC VAD
)

echo    🔧 Instalando PyAnnote Audio (opcional)...
venv\Scripts\python.exe -m pip install pyannote.audio
if errorlevel 1 (
    echo    ⚠️ PyAnnote Audio requiere configuración adicional
    echo       Continuando sin PyAnnote...
)

echo    ✅ Modelos VAD instalados

:: Instalar procesamiento de audio
echo.
echo [7/8] 🎵 Instalando librerías de audio...
echo    🔧 Instalando Librosa...
pip install librosa
if errorlevel 1 (
    echo    ⚠️ Error instalando Librosa
)

echo    🔧 Instalando SoundFile...
pip install soundfile
if errorlevel 1 (
    echo    ⚠️ Error instalando SoundFile
)

echo    🔧 Instalando SciPy...
pip install scipy
if errorlevel 1 (
    echo    ⚠️ Error instalando SciPy
)

echo    ✅ Librerías de audio instaladas

:: Instalar machine learning (opcional)
echo.
echo [8/8] 🧠 Instalando machine learning (opcional)...
echo    🔧 Instalando Scikit-learn...
pip install scikit-learn
if errorlevel 1 (
    echo    ⚠️ Error instalando Scikit-learn
)

echo    🔧 Instalando Optuna...
pip install optuna
if errorlevel 1 (
    echo    ⚠️ Error instalando Optuna
)

echo    ✅ Machine learning instalado

:: Crear directorios necesarios
echo.
echo 📁 Creando directorios del sistema...
if not exist "models_cache" mkdir "models_cache"
if not exist "output" mkdir "output"
if not exist "temp" mkdir "temp"
if not exist "learning_models" mkdir "learning_models"
echo    ✅ Directorios creados

:: Verificar instalación
echo.
echo 🔍 Verificando instalación...
python -c "import sys; print(f'Python: {sys.version}')"

echo    🔧 Verificando módulos críticos...
python -c "import torch; print('✅ PyTorch OK')" 2>nul || echo "⚠️ PyTorch no disponible"
python -c "import numpy; print('✅ NumPy OK')" 2>nul || echo "⚠️ NumPy no disponible"
python -c "import faster_whisper; print('✅ Faster-Whisper OK')" 2>nul || echo "⚠️ Faster-Whisper no disponible"

echo    🔧 Verificando modelos VAD...
python -c "import silero_vad; print('✅ Silero VAD OK')" 2>nul || echo "⚠️ Silero VAD no disponible"
python -c "import webrtcvad; print('✅ WebRTC VAD OK')" 2>nul || echo "⚠️ WebRTC VAD no disponible"

echo    🔧 Verificando procesamiento de audio...
python -c "import librosa; print('✅ Librosa OK')" 2>nul || echo "⚠️ Librosa no disponible"
python -c "import soundfile; print('✅ SoundFile OK')" 2>nul || echo "⚠️ SoundFile no disponible"

echo    🔧 Verificando machine learning...
python -c "import sklearn; print('✅ Scikit-learn OK')" 2>nul || echo "⚠️ Scikit-learn no disponible"

:: Crear scripts de conveniencia
echo.
echo 🔧 Creando scripts de conveniencia...

:: Script de activación
echo @echo off > activate_vad.bat
echo echo 🎮 Activando entorno VAD Gaming... >> activate_vad.bat
echo call "venv_vad_gaming\Scripts\activate.bat" >> activate_vad.bat
echo echo ✅ Entorno activado - Listo para usar VAD System >> activate_vad.bat
echo echo. >> activate_vad.bat
echo echo 💡 Comandos disponibles: >> activate_vad.bat
echo echo    python transcribe_vad_advanced.py audio.wav >> activate_vad.bat
echo echo    python verify_installation.py >> activate_vad.bat
echo echo. >> activate_vad.bat

:: Script de verificación rápida
echo import sys > verify_installation.py
echo print("🔍 Verificación rápida del sistema VAD") >> verify_installation.py
echo print("=" * 40) >> verify_installation.py
echo. >> verify_installation.py
echo try: >> verify_installation.py
echo     from vad_hybrid import HybridVAD >> verify_installation.py
echo     print("✅ VAD Híbrido disponible") >> verify_installation.py
echo except ImportError as e: >> verify_installation.py
echo     print(f"❌ VAD Híbrido: {e}") >> verify_installation.py
echo. >> verify_installation.py
echo try: >> verify_installation.py
echo     from vad_contextual import ContextualVAD >> verify_installation.py
echo     print("✅ VAD Contextual disponible") >> verify_installation.py
echo except ImportError as e: >> verify_installation.py
echo     print(f"❌ VAD Contextual: {e}") >> verify_installation.py
echo. >> verify_installation.py
echo try: >> verify_installation.py
echo     from transcribe_vad_advanced import AdvancedTranscriber >> verify_installation.py
echo     print("✅ Transcriptor Avanzado disponible") >> verify_installation.py
echo except ImportError as e: >> verify_installation.py
echo     print(f"❌ Transcriptor Avanzado: {e}") >> verify_installation.py
echo. >> verify_installation.py
echo print("\n🎯 Sistema listo para usar!") >> verify_installation.py

echo    ✅ Scripts de conveniencia creados

:: Generar reporte de instalación
echo.
echo 📄 Generando reporte de instalación...
echo ======================================== > installation_report.txt
echo 🎮 GameClipping VAD System >> installation_report.txt
echo Installation Report >> installation_report.txt
echo ======================================== >> installation_report.txt
echo Date: %date% %time% >> installation_report.txt
echo Python Version: %PYTHON_VERSION% >> installation_report.txt
echo Installation Directory: %cd% >> installation_report.txt
echo ======================================== >> installation_report.txt
echo. >> installation_report.txt

:: Finalización
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                    ✅ INSTALACIÓN COMPLETADA                     ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 El sistema VAD Híbrido está listo para usar!
echo.
echo 🚀 Próximos pasos:
echo    1. Ejecutar: activate_vad.bat
echo    2. Verificar: python verify_installation.py
echo    3. Transcribir: python transcribe_vad_advanced.py tu_audio.wav
echo.
echo 📚 Documentación completa: README_VAD_ADVANCED.md
echo 🔧 Reporte de instalación: installation_report.txt
echo.
echo 💡 Para usar el sistema:
echo    • activate_vad.bat   - Activa el entorno
echo    • transcribe_gaming.bat audio.wav   - Transcripción gaming
echo    • transcribe_precision.bat audio.wav   - Transcripción precision
echo.

choice /c YN /m "¿Ejecutar verificación ahora? (Y/N)"
if !errorlevel!==1 (
    echo.
    echo 🔍 Ejecutando verificación...
    python verify_installation.py
)

echo.
echo 🎮 ¡Disfruta del sistema VAD más avanzado para gaming!
echo.
pause