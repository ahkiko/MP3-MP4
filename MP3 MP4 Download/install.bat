@echo off
:: FFmpeg Installer Script for Windows
:: This script downloads and installs FFmpeg for your Discord MP3 bot

echo Checking if FFmpeg is already installed...
where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    echo FFmpeg is already installed!
    pause
    exit /b
)

echo Downloading FFmpeg...
mkdir ffmpeg_temp
cd ffmpeg_temp

:: Download FFmpeg build (using the official gyan.dev builds)
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'"

echo Extracting FFmpeg...
powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath ."

echo Installing FFmpeg...
:: Find the extracted folder
for /d %%i in (*) do set "folder=%%i"
cd "%folder%\bin"

:: Copy to Windows system folder (requires admin)
xcopy /y ffmpeg.exe "%SystemRoot%\System32\"
xcopy /y ffprobe.exe "%SystemRoot%\System32\"
xcopy /y ffplay.exe "%SystemRoot%\System32\"

echo Cleaning up...
cd ..\..\..
rd /s /q ffmpeg_temp

echo FFmpeg has been installed successfully!
echo Please restart any open command prompts for changes to take effect.
pause