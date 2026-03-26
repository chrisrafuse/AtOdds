#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy AtOdds to Railway from your local machine or a private GitHub repo.

.DESCRIPTION
    Prerequisites:
      1. Install Railway CLI: https://docs.railway.app/develop/cli
         winget install Railway.RailwayCLI   (or: npm i -g @railway/cli)
      2. railway login
      3. Copy .env.example to .env and fill in your API keys

.EXAMPLE
    # First deploy (creates a new project)
    .\deploy-railway.ps1 -FirstDeploy

    # Re-deploy after code changes
    .\deploy-railway.ps1
#>

param(
    [switch]$FirstDeploy
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "🚀 AtOdds — Railway Deployment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check Railway CLI is installed
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Error "Railway CLI not found. Install with: winget install Railway.RailwayCLI"
}

# Load .env if present
$EnvFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $EnvFile) {
    Write-Host "📄 Loading .env variables..." -ForegroundColor Yellow
    Get-Content $EnvFile | Where-Object { $_ -notmatch "^\s*#" -and $_ -match "=" } | ForEach-Object {
        $parts = $_ -split "=", 2
        if ($parts.Count -eq 2 -and $parts[0].Trim()) {
            [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim())
        }
    }
}

if ($FirstDeploy) {
    Write-Host "🔧 Creating new Railway project..." -ForegroundColor Yellow
    railway init
}

Write-Host "🔗 Linking to Railway project..." -ForegroundColor Yellow
railway link

# Set environment variables on Railway from local .env
if (Test-Path $EnvFile) {
    Write-Host "🔐 Pushing environment variables to Railway..." -ForegroundColor Yellow
    $LlmProvider = [Environment]::GetEnvironmentVariable("LLM_PROVIDER")
    if ($LlmProvider) { railway variables set "LLM_PROVIDER=$LlmProvider" }

    $OpenaiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY")
    if ($OpenaiKey -and $OpenaiKey -ne "sk-...") {
        railway variables set "OPENAI_API_KEY=$OpenaiKey"
        Write-Host "  ✓ OPENAI_API_KEY set" -ForegroundColor Green
    }

    $AnthropicKey = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY")
    if ($AnthropicKey -and $AnthropicKey -ne "sk-ant-...") {
        railway variables set "ANTHROPIC_API_KEY=$AnthropicKey"
        Write-Host "  ✓ ANTHROPIC_API_KEY set" -ForegroundColor Green
    }

    $GeminiKey = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY")
    if ($GeminiKey -and $GeminiKey -ne "AI...") {
        railway variables set "GEMINI_API_KEY=$GeminiKey"
        Write-Host "  ✓ GEMINI_API_KEY set" -ForegroundColor Green
    }
}

Write-Host "📦 Deploying to Railway..." -ForegroundColor Yellow
railway up --detach

Write-Host ""
Write-Host "✅ Deployment triggered!" -ForegroundColor Green
Write-Host "   View logs:   railway logs" -ForegroundColor Gray
Write-Host "   Open app:    railway open" -ForegroundColor Gray
Write-Host "   Get URL:     railway domain" -ForegroundColor Gray
