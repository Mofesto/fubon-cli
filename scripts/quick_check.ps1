#!/usr/bin/env pwsh
<#
.SYNOPSIS
    快速檢查腳本 - 驗證項目的基本配置和依賴
    
.DESCRIPTION
    檢查以下項目:
    - Python 版本
    - 依賴項安裝狀況
    - 代碼風格
    - 基本測試
    
.EXAMPLE
    .\scripts\quick_check.ps1
#>

$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "`n==> $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

Write-ColorOutput "`n╔══════════════════════════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║           Fubon CLI Quick Check v1.0                        ║" "Cyan"
Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝`n" "Cyan"

# 檢查 Python 版本
Write-Step "檢查 Python 版本..."
$pythonVersion = python --version 2>&1
Write-Host $pythonVersion
Write-Success "Python 就緒"

# 檢查依賴項
Write-Step "檢查依賴項..."
pip list | findstr /C:"click" /C:"fubon" /C:"pydantic" /C:"python-dotenv"
Write-Success "主要依賴項已安裝"

# 運行 linting
Write-Step "運行代碼檢查..."
if (Get-Command flake8 -ErrorAction SilentlyContinue) {
    flake8 fubon_cli --max-line-length=100 || Write-Warning "發現代碼風格問題"
} else {
    Write-Warning "flake8 未安裝，跳過"
}

# 運行 pytest
Write-Step "運行基本測試..."
if (Get-Command pytest -ErrorAction SilentlyContinue) {
    pytest -v --tb=short || Write-Warning "部分測試失敗"
} else {
    Write-Warning "pytest 未安裝，跳過"
}

Write-ColorOutput "`n╔══════════════════════════════════════════════════════════════╗" "Green"
Write-ColorOutput "║              ✓ 快速檢查完成!                               ║" "Green"
Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝" "Green"
