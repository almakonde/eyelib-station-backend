poetry config virtualenvs.in-project true
poetry install --dry-run --no-dev
poetry run python -m pip install --upgrade pip
poetry install --no-dev

REM Add desktop shortcut

powershell Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\utils\shortcut.ps1 .\tray.bat "$( (Join-Path (Resolve-Path ~\Desktop).Path Station-Backend.lnk))" .\
powershell Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\utils\shortcut.ps1 .\tray.bat "\"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\Station-Backend.lnk\"" .\