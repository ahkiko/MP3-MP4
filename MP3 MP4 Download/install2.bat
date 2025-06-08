@echo off
:: YouTube-DL Installer for Windows
:: This script installs yt-dlp (best youtube-dl fork) and FFmpeg
:: Run as Administrator for best results

echo #############################################
echo #   YouTube-DL/FFmpeg Windows Installer     #
echo #############################################
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b
)

:: Set variables
set "YTDLP_URL=https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
set "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"
set "INSTALL_DIR=%ProgramFiles%\yt-dlp"
set "TEMP_DIR=%TEMP%\yt-dlp-install"

:: Create directories
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%TEMP_DIR%" 2>nul

:: Download yt-dlp
echo Downloading yt-dlp...
powershell -Command "(New-Object Net.WebClient).DownloadFile('%YTDLP_URL%', '%TEMP_DIR%\yt-dlp.exe')"

:: Download FFmpeg
echo Downloading FFmpeg...
powershell -Command "(New-Object Net.WebClient).DownloadFile('%FFMPEG_URL%', '%TEMP_DIR%\ffmpeg.7z')"

:: Install 7-Zip if needed (to extract FFmpeg)
where 7z >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing 7-Zip...
    winget install 7zip.7zip -h --accept-source-agreements --accept-package-agreements
)

:: Extract FFmpeg
echo Extracting FFmpeg...
7z x "%TEMP_DIR%\ffmpeg.7z" -o"%TEMP_DIR%\ffmpeg" -y >nul

:: Copy files to installation directory
echo Installing files...
copy "%TEMP_DIR%\yt-dlp.exe" "%INSTALL_DIR%\yt-dlp.exe" >nul
xcopy "%TEMP_DIR%\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\*" "%INSTALL_DIR%\" /s /y >nul

:: Add to PATH
echo Adding to system PATH...
setx /M PATH "%PATH%;%INSTALL_DIR%"

:: Cleanup
echo Cleaning up...
rmdir /s /q "%TEMP_DIR%"

echo.
echo Installation complete!
echo yt-dlp and FFmpeg have been installed to: %INSTALL_DIR%
echo.
echo Examples:
echo   yt-dlp "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -f best
echo   yt-dlp -x --audio-format mp3 "https://youtu.be/VIDEO_ID"
echo.
pause