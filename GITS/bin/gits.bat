
---BATCH_SCRIPT---
@echo off
REM gits.bat - Launch Git Python GUI (Batch script for Windows)
REM Usage: gits [repository_path]
REM If no path provided, uses current directory

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Remove trailing backslash
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Path to the Python GUI script
set "GUI_SCRIPT=%SCRIPT_DIR%\git_python_gui.py"

REM Check if the GUI script exists
if not exist "%GUI_SCRIPT%" (
    echo Error: git_python_gui.py not found in %SCRIPT_DIR%
    echo Please ensure git_python_gui.py is in the same directory as this script.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python not found. Please install Python 3.
        echo You can download it from https://python.org
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)

REM Check if gitpython is installed
%PYTHON_CMD% -c "import git" >nul 2>&1
if errorlevel 1 (
    echo Error: GitPython not installed. Please install it with:
    echo pip install gitpython
    pause
    exit /b 1
)

REM Launch the GUI with arguments
if "%~1"=="" (
    REM No arguments, use current directory
    echo Launching Git GUI in current directory...
    %PYTHON_CMD% "%GUI_SCRIPT%" "%CD%"
) else (
    REM Pass all arguments to the Python script
    echo Launching Git GUI with path: %1
    %PYTHON_CMD% "%GUI_SCRIPT%" %*
)