#!/usr/bin/env pwsh
<#
.SYNOPSIS
    更新版本號腳本
    
.PARAMETER NewVersion
    新版本號，格式: major.minor.patch (例如: 0.2.0)
    
.EXAMPLE
    .\scripts\update_version.ps1 -NewVersion "0.2.0"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$NewVersion
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# 驗證版本格式
if ($NewVersion -notmatch '^\d+\.\d+\.\d+$') {
    Write-ColorOutput "❌ 版本格式錯誤, 應為: major.minor.patch" "Red"
    exit 1
}

Write-ColorOutput "`n更新版本到 $NewVersion..." "Cyan"

# 更新 version_config.json
$configPath = Join-Path $ScriptDir "version_config.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$config.version.current = $NewVersion
$config | ConvertTo-Json | Set-Content $configPath -Encoding UTF8

Write-ColorOutput "✓ 版本已更新到 $NewVersion" "Green"
Write-Host "已修改: $configPath"
