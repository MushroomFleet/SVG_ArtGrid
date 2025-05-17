@echo off
echo Creating virtual environment...
python -m venv "%~dp0artgrid-env"

echo Activating virtual environment...
call "%~dp0artgrid-env\Scripts\activate.bat"

echo Installing required packages...
pip install -r "%~dp0requirements.txt"

echo.
echo Installation complete! 
echo.
echo To activate the environment in future sessions:
echo   call "%~dp0artgrid-env\Scripts\activate.bat"
echo.
echo Example usage after activation:
echo   python "%~dp0SVGArtGridV2.py" --image "%~dp0alpha.png" --mode palette
echo.
pause
