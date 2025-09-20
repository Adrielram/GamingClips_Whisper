@echo off
REM Crea un acceso directo en el escritorio para transcribir videos
REM Solo ejecuta este archivo una vez para configurar el acceso directo

echo 🎮 Creando acceso directo para transcripción de videos...

set "SCRIPT_PATH=%~dp0transcribe.bat"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Transcribir Video Gaming.lnk"

REM Crear acceso directo usando PowerShell
powershell -Command ^
"$WshShell = New-Object -comObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); ^
$Shortcut.TargetPath = '%SCRIPT_PATH%'; ^
$Shortcut.WorkingDirectory = '%~dp0'; ^
$Shortcut.Description = 'Arrastra un video aquí para transcribirlo automáticamente'; ^
$Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo ✅ Acceso directo creado en el escritorio: "Transcribir Video Gaming"
    echo.
    echo 🎯 Ahora puedes:
    echo     1. Arrastrar videos directamente al icono del escritorio
    echo     2. O arrastrar videos al archivo transcribe.bat
    echo.
    echo 💡 Formatos soportados: .mp4, .mkv, .mov, .avi, .webm, .mp3, .wav, etc.
) else (
    echo ❌ Error al crear el acceso directo
)

echo.
pause