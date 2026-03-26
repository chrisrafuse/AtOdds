#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup AtOdds full server with Python 3.12 and LLM providers

.DESCRIPTION
    1. Install Python 3.12 from Microsoft Store
    2. Create virtual environment
    3. Install dependencies
    4. Configure environment variables
    5. Run full server
#>

Write-Host "🚀 AtOdds Full Server Setup" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Check Python 3.12
Write-Host "📋 Checking Python 3.12..." -ForegroundColor Yellow
try {
    $py312 = py -3.12 --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python 3.12 found: $py312" -ForegroundColor Green
    } else {
        Write-Host "❌ Python 3.12 not found" -ForegroundColor Red
        Write-Host "Please install Python 3.12 from Microsoft Store first:" -ForegroundColor Yellow
        Write-Host "https://www.microsoft.com/store/productId/9MSSZNGCNK0F" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "❌ Error checking Python 3.12" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Removing existing venv..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}
py -3.12 -m venv venv

# Activate and install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements-web.txt

# Setup environment
Write-Host "🔧 Setting up environment..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
    Write-Host "Edit .env to add your LLM API keys:" -ForegroundColor Yellow
    Write-Host "  LLM_PROVIDER=openai|anthropic|gemini|mock" -ForegroundColor Gray
    Write-Host "  OPENAI_API_KEY=sk-..." -ForegroundColor Gray
    Write-Host "  ANTHROPIC_API_KEY=sk-ant-..." -ForegroundColor Gray
    Write-Host "  GEMINI_API_KEY=AI..." -ForegroundColor Gray
} else {
    Write-Host ".env already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the full server:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  python -m apps.web.run_api" -ForegroundColor Gray
Write-Host ""
Write-Host "Or run this script with -Run flag to start immediately:" -ForegroundColor Yellow
Write-Host "  .\setup_full_server.ps1 -Run" -ForegroundColor Gray

if ($args -contains "-Run") {
    Write-Host ""
    Write-Host "🚀 Starting full server..." -ForegroundColor Cyan
    python -m apps.web.run_api
}
