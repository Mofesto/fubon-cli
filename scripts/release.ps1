#!/usr/bin/env pwsh
<#
.SYNOPSIS
    自動版本發布腳本 v1.0
    
.DESCRIPTION
    此腳本用於自動化版本發布流程:
    1. 執行完整的 CI 測試
    2. 更新版本號
    3. 生成 Release Notes
    4. 創建 Git 標籤
    5. 推送到 GitHub 觸發自動發布
    
.PARAMETER BumpType
    版本進版類型: patch (預設), minor, 或 major
    - patch: 0.1.0 -> 0.1.1 (小修復)
    - minor: 0.1.0 -> 0.2.0 (新功能)
    - major: 0.1.0 -> 1.0.0 (重大更新)
    
.PARAMETER SkipTests
    跳過測試直接發布 (不建議)
    
.PARAMETER SkipVersionUpdate
    跳過版本更新 (僅用於測試)
    
.EXAMPLE
    .\scripts\release.ps1
    # 發布 patch 版本 (預設)
    
.EXAMPLE
    .\scripts\release.ps1 -BumpType minor
    # 發布 minor 版本
    
.EXAMPLE
    .\scripts\release.ps1 -BumpType major
    # 發布 major 版本
#>

param(
    [Parameter()]
    [ValidateSet("patch", "minor", "major")]
    [string]$BumpType = "patch",
    
    [Parameter()]
    [switch]$SkipTests,
    
    [Parameter()]
    [switch]$SkipVersionUpdate
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# 顏色輸出函數
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

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" "Yellow"
}

# 讀取版本配置
function Get-VersionConfig {
    $configPath = Join-Path $ScriptDir "version_config.json"
    return Get-Content $configPath -Raw | ConvertFrom-Json
}

# 檢查 Git 狀態
function Test-GitStatus {
    Write-Step "檢查 Git 狀態..."
    
    $status = git status --porcelain
    if ($status) {
        Write-Warning "Working directory 有未提交的更改"
        Write-Host $status
        $continue = Read-Host "是否繼續? (y/n)"
        if ($continue -ne "y") {
            exit 1
        }
    }
    Write-Success "Git 狀態檢查完成"
}

# 執行測試
function Invoke-Tests {
    if ($SkipTests) {
        Write-Warning "跳過測試..."
        return
    }
    
    Write-Step "執行測試..."
    
    # 安装測試依賴
    pip install -q pytest pytest-cov pytest-xdist pytest-mock
    
    # 運行測試
    pytest -v --cov=fubon_cli --cov-report=term-missing --cov-report=html
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "測試失敗，終止發布"
        exit 1
    }
    
    Write-Success "所有測試通過"
}

# 計算新版本號
function Get-NewVersion {
    param([string]$CurrentVersion)
    
    $parts = $CurrentVersion.Split('.')
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]
    
    switch ($BumpType) {
        "major" {
            $major += 1
            $minor = 0
            $patch = 0
        }
        "minor" {
            $minor += 1
            $patch = 0
        }
        "patch" {
            $patch += 1
        }
    }
    
    return "$major.$minor.$patch"
}

# 更新版本配置
function Update-VersionConfig {
    param([string]$NewVersion)
    
    if ($SkipVersionUpdate) {
        Write-Warning "跳過版本配置更新..."
        return
    }
    
    Write-Step "更新版本配置為 $NewVersion..."
    
    $configPath = Join-Path $ScriptDir "version_config.json"
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
    $config.version.current = $NewVersion
    
    $config | ConvertTo-Json | Set-Content $configPath -Encoding UTF8
    Write-Success "版本配置已更新"
}

# 提交更改
function Invoke-GitCommit {
    param([string]$Version)
    
    Write-Step "提交更改..."
    
    git add .
    git commit -m "chore: bump version to $Version" --no-verify
    
    Write-Success "更改已提交"
}

# 創建標籤
function New-GitTag {
    param([string]$Version)
    
    Write-Step "創建 Git 標籤 v$Version..."
    
    $tagName = "v$Version"
    git tag -a $tagName -m "Release version $Version"
    
    Write-Success "標籤創建完成"
}

# 推送到 GitHub
function Push-ToGitHub {
    param([string]$Version)
    
    Write-Step "推送到 GitHub..."
    
    git push origin main --no-verify
    git push origin "v$Version" --no-verify
    
    Write-Success "推送完成，GitHub Actions 將自動構建和發佈"
}

# 生成 Release Notes
function Get-ReleaseNotes {
    param([string]$Version)
    
    Write-Step "生成 Release Notes..."
    
    $changeLog = "## Version $Version`n`n"
    $changeLog += "### Changes`n"
    $changeLog += "- Update version to $Version`n`n"
    $changeLog += "See full changelog in [CHANGELOG.md](./CHANGELOG.md)`n"
    
    return $changeLog
}

# 主函數
function Invoke-ReleaseWorkflow {
    Write-ColorOutput "`n╔══════════════════════════════════════════════════════════════╗" "Cyan"
    Write-ColorOutput "║           Fubon CLI Release Automation v1.0                ║" "Cyan"
    Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝`n" "Cyan"
    
    $config = Get-VersionConfig
    $currentVersion = $config.version.current
    $newVersion = Get-NewVersion $currentVersion
    
    Write-ColorOutput "當前版本: $currentVersion" "Yellow"
    Write-ColorOutput "新版本: $newVersion" "Yellow"
    Write-ColorOutput "進版類型: $BumpType" "Yellow"
    
    Write-Host "`n"
    $confirm = Read-Host "確認發布? (y/n)"
    if ($confirm -ne "y") {
        Write-Warning "發布已取消"
        exit 0
    }
    
    try {
        Test-GitStatus
        Invoke-Tests
        Update-VersionConfig $newVersion
        Invoke-GitCommit $newVersion
        New-GitTag $newVersion
        Push-ToGitHub $newVersion
        
        Write-ColorOutput "`n╔══════════════════════════════════════════════════════════════╗" "Green"
        Write-ColorOutput "║              ✓ 發布流程完成! Version $newVersion              ║" "Green"
        Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝" "Green"
        
        Write-Host "`n檢查 GitHub Actions: https://github.com/mofesto/fubon-cli/actions"
        
    } catch {
        Write-ErrorMsg "發布失敗: $_"
        exit 1
    }
}

# 執行主程序
Invoke-ReleaseWorkflow
