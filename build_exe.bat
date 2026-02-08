@echo off
echo Building WMS.exe...
rem Note: To set the .exe file icon, convert app_icon.jpg to .ico and add: --icon "icons/app_icon.ico"
pyinstaller --noconfirm --onefile --windowed --name "WMS_System" --add-data "icons;icons" main.py
echo Build complete. Check the 'dist' folder.
pause
