@echo off
echo Building Dr.Ist Game...
echo.

REM Проверка наличия PyInstaller и Pillow
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

python -c "from PIL import Image" 2>nul
if errorlevel 1 (
    echo Installing Pillow...
    pip install Pillow
)

REM Создание .exe файла
pyinstaller --name "Dr.Ist Game" ^
    --icon=icon.ico ^
    --add-data "mixkit-completion-of-a-level-2063.wav;." ^
    --add-data "mixkit-player-losing-or-failing-2042.wav;." ^
    --add-data "mixkit-unlock-game-notification-253.wav;." ^
    --add-data "Qumu - Sweden.mp3;." ^
    --noconsole ^
    --onefile ^
    game.py

echo.
if errorlevel 1 (
    echo Build failed!
    pause
) else (
    echo Build completed successfully!
    echo The executable file is located in the dist folder
    pause
)
