@echo off
echo Creating virtual environment for AtOdds Web API...
if not exist .venv (
    python -m venv .venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install python-multipart
pip install fastapi uvicorn pydantic pydantic-settings
pip install pytest pytest-asyncio httpx

echo.
echo Virtual environment setup complete!
echo.
echo To start the API server:
echo python apps/web/run_api.py
echo.
echo To run tests:
echo python -m pytest tests/test_api_endpoints.py -v
echo.
pause
