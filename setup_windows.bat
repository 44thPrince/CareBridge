@echo off
echo =========================================
echo    CareBridge Windows Setup Script
echo =========================================
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.13+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM Check PostgreSQL
echo [2/6] Checking PostgreSQL installation...
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] PostgreSQL not found in PATH!
    echo If PostgreSQL is installed, add to PATH:
    echo C:\Program Files\PostgreSQL\16\bin
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    psql --version
)
echo.

REM Create virtual environment
echo [3/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)
echo.

REM Activate virtual environment and install dependencies
echo [4/6] Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

REM Create .env file if it doesn't exist
echo [5/6] Setting up environment variables...
if exist .env (
    echo .env file already exists. Skipping...
) else (
    copy .env.example .env >nul 2>&1
    if exist .env.example (
        echo .env file created from template
        echo [ACTION REQUIRED] Please edit .env and add:
        echo   - DB_PASSWORD (your PostgreSQL password)
        echo   - GOOGLE_API_KEY (from https://aistudio.google.com/app/apikey)
    ) else (
        echo [WARNING] .env.example not found
        echo Please create .env file manually
    )
)
echo.

REM Database setup
echo [6/6] Database setup...
set /p setup_db="Do you want to set up the database now? (y/n): "
if /i "%setup_db%"=="y" (
    set /p db_password="Enter PostgreSQL password for user 'postgres': "
    
    echo Setting up database...
    set PGPASSWORD=%db_password%
    psql -U postgres -f seed.sql
    
    if %errorlevel% equ 0 (
        echo Database setup complete!
    ) else (
        echo [ERROR] Database setup failed
        echo You can run this manually later:
        echo   psql -U postgres -f seed.sql
    )
) else (
    echo Skipping database setup
    echo Run manually later: psql -U postgres -f seed.sql
)
echo.

echo =========================================
echo    Setup Complete!
echo =========================================
echo.
echo Next steps:
echo 1. Edit .env file with your credentials
echo    - DB_PASSWORD=your_postgres_password
echo    - GOOGLE_API_KEY=your_google_api_key
echo.
echo 2. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 3. Run the application:
echo    python app.py
echo.
echo 4. Visit in browser:
echo    http://localhost:5003
echo.
echo 5. Test AI matching:
echo    python matching_agent.py 1
echo.
echo Default login credentials:
echo   Username: admin
echo   Password: secret123
echo.
pause