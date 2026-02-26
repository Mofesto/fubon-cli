<#
.SYNOPSIS
    Test fubon-cli commands with real data scenarios

.DESCRIPTION
    This script tests various fubon-cli commands to verify they handle real data correctly.
    It checks:
    - Command execution and JSON output
    - Error handling
    - Data format validation
    - Common use cases

.NOTES
    Before running this script:
    1. Ensure you are logged in: fubon login --id <ID> --password <PW> --cert-path <PATH>
    2. Or set credentials in environment variables for testing
#>

param(
    [switch]$SkipLogin,
    [string]$TestSymbol = "2330",  # Taiwan Semiconductor (default test symbol)
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$script:TestResults = @()

function Write-TestHeader {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Output,
        [string]$ErrorMessage
    )
    
    $result = [PSCustomObject]@{
        TestName = $TestName
        Passed = $Passed
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Output = $Output
        Error = $ErrorMessage
    }
    
    $script:TestResults += $result
    
    if ($Passed) {
        Write-Host "✓ PASS: $TestName" -ForegroundColor Green
    } else {
        Write-Host "✗ FAIL: $TestName" -ForegroundColor Red
        if ($ErrorMessage) {
            Write-Host "  Error: $ErrorMessage" -ForegroundColor Red
        }
    }
    
    if ($Verbose -and $Output) {
        Write-Host "  Output: $($Output.Substring(0, [Math]::Min(200, $Output.Length)))" -ForegroundColor Gray
    }
}

function Test-JSONOutput {
    param([string]$Output)
    
    try {
        $null = $Output | ConvertFrom-Json
        return $true
    } catch {
        return $false
    }
}

function Test-Command {
    param(
        [string]$TestName,
        [string]$Command,
        [scriptblock]$ValidationScript = { $true }
    )
    
    Write-Host "Testing: $TestName..." -NoNewline
    
    try {
        $output = Invoke-Expression $Command 2>&1 | Out-String
        $isValidJSON = Test-JSONOutput -Output $output
        $customValidation = & $ValidationScript $output
        
        $passed = $isValidJSON -and $customValidation
        Write-TestResult -TestName $TestName -Passed $passed -Output $output -Error $(if (-not $passed) { "Invalid JSON or validation failed" } else { "" })
        
        return $passed
    } catch {
        Write-TestResult -TestName $TestName -Passed $false -Output "" -Error $_.Exception.Message
        return $false
    }
}

# Start testing
Write-Host "`n🧪 Fubon CLI Real Data Testing Script" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Test 1: CLI Version
Write-TestHeader "Test 1: Basic CLI Functionality"
Test-Command `
    -TestName "CLI Version Check" `
    -Command "fubon --version" `
    -ValidationScript { param($output) $output -match '\d+\.\d+\.\d+' }

# Test 2: Login Status
Write-TestHeader "Test 2: Authentication Status"
Test-Command `
    -TestName "Login Status Check" `
    -Command "fubon login status"

# Test 3: Market Data - Quote
Write-TestHeader "Test 3: Market Data Commands"
Test-Command `
    -TestName "Get Stock Quote ($TestSymbol)" `
    -Command "fubon market quote $TestSymbol" `
    -ValidationScript { 
        param($output)
        try {
            $data = $output | ConvertFrom-Json
            return $data.success -eq $true -or ($data.PSObject.Properties.Name -contains 'symbol')
        } catch {
            return $false
        }
    }

Test-Command `
    -TestName "Get Stock Ticker ($TestSymbol)" `
    -Command "fubon market ticker $TestSymbol"

Test-Command `
    -TestName "Get Stock Candles ($TestSymbol)" `
    -Command "fubon market candles $TestSymbol --timeframe 5"

# Test 4: Market Snapshot
Test-Command `
    -TestName "Get Market Snapshot (TSE)" `
    -Command "fubon market snapshot TSE"

# Test 5: Account Commands (Read-only)
Write-TestHeader "Test 4: Account Information"
Test-Command `
    -TestName "Get Account Inventory" `
    -Command "fubon account inventory" `
    -ValidationScript {
        param($output)
        try {
            $null = $output | ConvertFrom-Json
            # Should return either success:true or an array
            return $true
        } catch {
            return $false
        }
    }

Test-Command `
    -TestName "Get Unrealized P&L" `
    -Command "fubon account unrealized"

Test-Command `
    -TestName "Get Settlement Info" `
    -Command "fubon account settlement"

# Test 6: Order Query (Read-only)
Write-TestHeader "Test 5: Order Management (Read-only)"
Test-Command `
    -TestName "Query Current Orders" `
    -Command "fubon stock orders"

# Test 7: Edge Cases
Write-TestHeader "Test 6: Edge Cases and Error Handling"
Test-Command `
    -TestName "Invalid Symbol Handling" `
    -Command "fubon market quote INVALID999" `
    -ValidationScript {
        param($output)
        # Should still return valid JSON, potentially with error
        try {
            $null = $output | ConvertFrom-Json
            return $true
        } catch {
            return $false
        }
    }

Test-Command `
    -TestName "Missing Required Parameter" `
    -Command "fubon market quote" `
    -ValidationScript {
        param($output)
        # Should return error in some form
        return $output.Length -gt 0
    }

# Test 8: Help Commands
Write-TestHeader "Test 7: Help and Documentation"
Test-Command `
    -TestName "Main Help" `
    -Command "fubon --help" `
    -ValidationScript { param($output) $output -match 'Usage:' }

Test-Command `
    -TestName "Stock Command Help" `
    -Command "fubon stock --help" `
    -ValidationScript { param($output) $output -match 'buy|sell|orders' }

Test-Command `
    -TestName "Market Command Help" `
    -Command "fubon market --help" `
    -ValidationScript { param($output) $output -match 'quote|ticker|candles' }

# Generate Summary Report
Write-Host "`n" 
Write-TestHeader "Test Summary Report"

$totalTests = $script:TestResults.Count
$passedTests = ($script:TestResults | Where-Object { $_.Passed }).Count
$failedTests = $totalTests - $passedTests
$passRate = if ($totalTests -gt 0) { [math]::Round(($passedTests / $totalTests) * 100, 2) } else { 0 }

Write-Host "Total Tests:  $totalTests" -ForegroundColor White
Write-Host "Passed:       $passedTests" -ForegroundColor Green
Write-Host "Failed:       $failedTests" -ForegroundColor $(if ($failedTests -gt 0) { "Red" } else { "Green" })
Write-Host "Pass Rate:    $passRate%" -ForegroundColor $(if ($passRate -ge 80) { "Green" } elseif ($passRate -ge 60) { "Yellow" } else { "Red" })

# Export results to JSON
$reportPath = Join-Path $PSScriptRoot "test_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$script:TestResults | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "`nDetailed results saved to: $reportPath" -ForegroundColor Cyan

# Show failed tests details
if ($failedTests -gt 0) {
    Write-Host "`n❌ Failed Tests Details:" -ForegroundColor Red
    $script:TestResults | Where-Object { -not $_.Passed } | ForEach-Object {
        Write-Host "  - $($_.TestName)" -ForegroundColor Red
        if ($_.Error) {
            Write-Host "    Error: $($_.Error)" -ForegroundColor Gray
        }
    }
}

Write-Host "`n✨ Testing Complete!" -ForegroundColor Cyan

# Exit with appropriate code
exit $(if ($failedTests -eq 0) { 0 } else { 1 })
