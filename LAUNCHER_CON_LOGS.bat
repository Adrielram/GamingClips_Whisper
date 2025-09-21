@echo off
echo.
echo 🔧 SISTEMA DE TRANSCRIPCIÓN CON LOGGING AVANZADO
echo ============================================
echo.
echo 💡 Selecciona una opción:
echo.
echo 1. 🖥️  Interfaz Visual (GUI) - Recomendada
echo 2. 💻 Interfaz de Consola (CLI) - Alternativa
echo 3. 🧪 Probar Sistema de Logging
echo 4. 📋 Ver Logs Existentes
echo 5. 🧹 Limpiar Logs Antiguos
echo 6. ❌ Salir
echo.

:MENU
set /p choice="Selecciona una opción (1-6): "

if "%choice%"=="1" goto GUI
if "%choice%"=="2" goto CLI
if "%choice%"=="3" goto TEST_LOGGING
if "%choice%"=="4" goto VIEW_LOGS
if "%choice%"=="5" goto CLEAN_LOGS
if "%choice%"=="6" goto EXIT

echo ❌ Opción inválida. Intenta de nuevo.
goto MENU

:GUI
echo.
echo 🖥️ Abriendo Interfaz Visual...
echo 📝 Los logs se guardarán en la carpeta 'logs\'
echo.

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python transcription_gui.py
goto END

:CLI
echo.
echo 💻 Abriendo Interfaz de Consola...
echo 📝 Los logs se guardarán en la carpeta 'logs\'
echo.

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python transcription_cli.py
goto END

:TEST_LOGGING
echo.
echo 🧪 Probando Sistema de Logging...
echo.

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python test_logging.py
echo.
pause
goto MENU

:VIEW_LOGS
echo.
echo 📋 LOGS EXISTENTES:
echo ==================
echo.

if exist "logs\" (
    dir logs\ /b /o:d
    echo.
    echo 📂 Ubicación: %CD%\logs\
    echo.
    echo 💡 Tipos de archivos:
    echo    • transcription_*.log - Log general completo
    echo    • errors_*.log - Solo errores
    echo    • session_summary_*.json - Resumen en formato JSON
) else (
    echo ❌ No hay carpeta de logs aún
    echo 💡 Se creará automáticamente al ejecutar transcripciones
)

echo.
pause
goto MENU

:CLEAN_LOGS
echo.
echo 🧹 Limpiando logs antiguos...
echo.

if exist "logs\" (
    echo ⚠️ Esto eliminará TODOS los archivos de log existentes.
    set /p confirm="¿Estás seguro? (s/N): "
    
    if /i "%confirm%"=="s" (
        del /q logs\*.*
        echo ✅ Logs eliminados
    ) else (
        echo ❌ Operación cancelada
    )
) else (
    echo ❌ No hay carpeta de logs para limpiar
)

echo.
pause
goto MENU

:EXIT
echo.
echo 👋 ¡Hasta luego!
goto END

:END
echo.
echo 💡 TIP: Los logs detallados están en la carpeta 'logs\'
echo 💡 Revisa 'errors_*.log' para debugging de problemas específicos
echo.
pause