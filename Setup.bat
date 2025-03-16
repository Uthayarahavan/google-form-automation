@echo off
echo Setting up Google Forms Creation System...
powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1"
echo.
echo If the setup completed successfully, you can now run StartMenu.bat 