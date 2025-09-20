@echo off
REM Crea accesos directos en el escritorio para transcripción de videos
REM Ejecuta este archivo una vez para configurar los accesos directos

echo 🎮 Creando accesos directos para transcripción de videos...
echo.

set "SCRIPT_PATH=%~dp0transcribe.bat"
set "PRECISE_SCRIPT_PATH=%~dp0transcribe_precise.bat"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Transcribir Video Gaming.lnk"
set "PRECISE_SHORTCUT=%DESKTOP%\Transcribir Video ULTRA-PRECISO.lnk"

REM Crear acceso directo estándar
powershell -Command ^
"$WshShell = New-Object -comObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); ^
$Shortcut.TargetPath = '%SCRIPT_PATH%'; ^
$Shortcut.WorkingDirectory = '%~dp0'; ^
$Shortcut.Description = 'Arrastra un video aquí para transcribirlo (método estándar)'; ^
$Shortcut.Save()"

REM Crear acceso directo ultra-preciso
powershell -Command ^
"$WshShell = New-Object -comObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut('%PRECISE_SHORTCUT%'); ^
$Shortcut.TargetPath = '%PRECISE_SCRIPT_PATH%'; ^
$Shortcut.WorkingDirectory = '%~dp0'; ^
$Shortcut.Description = 'Arrastra un video aquí para transcripción ULTRA-PRECISA con sincronización perfecta'; ^
$Shortcut.Save()"

echo ✅ Accesos directos creados en el escritorio:
echo.
if exist "%SHORTCUT%" (
    echo 📋 "Transcribir Video Gaming" - Método estándar
    echo     • Rápido y eficiente
    echo     • Buena calidad general
    echo     • Recomendado para uso diario
)
echo.
if exist "%PRECISE_SHORTCUT%" (
    echo 🎯 "Transcribir Video ULTRA-PRECISO" - Máxima calidad
    echo     • Sincronización palabra por palabra
    echo     • Precisión de milisegundos
    echo     • Recomendado para contenido importante
)

echo.
echo 🎯 Ahora puedes:
echo     1. Arrastrar videos a cualquiera de los iconos del escritorio
echo     2. O usar los archivos .bat directamente en esta carpeta
echo.
echo 💡 Formatos soportados: .mp4, .mkv, .mov, .avi, .webm, .mp3, .wav, etc.
echo.
pause