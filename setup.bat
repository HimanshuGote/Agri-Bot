@echo off
REM Agriculture Chatbot - Windows Setup Script

echo ========================================
echo   Agriculture Chatbot - Setup Script
echo ========================================
echo.

REM Step 1: Check Python
echo Step 1: Checking Python Version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.9+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%
echo.

REM Step 2: Create virtual environment
echo Step 2: Creating Virtual Environment...
if exist venv\ (
    echo [WARN] Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

REM Step 3: Activate virtual environment
echo Step 3: Activating Virtual Environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Step 4: Upgrade pip
echo Step 4: Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo [OK] pip upgraded
echo.

REM Step 5: Install dependencies
echo Step 5: Installing Dependencies...
echo This may take 2-3 minutes...
if exist requirements.txt (
    pip install -r requirements.txt
    echo [OK] Dependencies installed
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)
echo.

REM Step 6: Check for PDF files
echo Step 6: Checking for PDF Files...
set PDF_COUNT=0

if exist CitrusPlantPestsAndDiseases.pdf (
    echo [OK] Found CitrusPlantPestsAndDiseases.pdf
    set /a PDF_COUNT+=1
) else (
    echo [ERROR] CitrusPlantPestsAndDiseases.pdf not found!
)

if exist GovernmentSchemes.pdf (
    echo [OK] Found GovernmentSchemes.pdf
    set /a PDF_COUNT+=1
) else (
    echo [ERROR] GovernmentSchemes.pdf not found!
)

if %PDF_COUNT% neq 2 (
    echo [WARN] Please place both PDF files in the project root.
)
echo.

REM Step 7: Set up environment variables
echo Step 7: Setting up Environment Variables...
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo [OK] Created .env file from .env.example
        echo [WARN] IMPORTANT: Edit .env and add your OPENAI_API_KEY!
    ) else (
        echo [ERROR] .env.example not found!
    )
) else (
    echo [OK] .env file already exists
)
echo.

REM Step 8: Create directories
echo Step 8: Creating Directory Structure...
if not exist chroma_db mkdir chroma_db
if not exist chroma_db\citrus_diseases mkdir chroma_db\citrus_diseases
if not exist chroma_db\government_schemes mkdir chroma_db\government_schemes
if not exist logs mkdir logs
echo [OK] Directory structure created
echo.

REM Summary
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo.
echo 1. Ensure both PDF files are in the project root
echo.
echo 2. Configure your OpenAI API key in .env:
echo    notepad .env
echo    (Set OPENAI_API_KEY=your-actual-key)
echo.
echo 3. Start the application:
echo    python main.py
echo    or
echo    uvicorn main:app --reload
echo.
echo 4. Access the API:
echo    http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo.
echo 5. Run tests:
echo    python test_queries.py
echo.
echo Useful Commands:
echo   Activate venv:   venv\Scripts\activate.bat
echo   Deactivate venv: deactivate
echo.
pause
