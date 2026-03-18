# Box Box Box - Test Runner

$TestCasesDir = "data/test_cases/inputs"
$ExpectedDir  = "data/test_cases/expected_outputs"

# --- Check test cases dir ---
if (-not (Test-Path $TestCasesDir)) {
    Write-Host "Error: Test cases directory not found: $TestCasesDir" -ForegroundColor Red
    exit 1
}

$TestFiles  = Get-ChildItem "$TestCasesDir/test_*.json" | Sort-Object Name
$TotalTests = $TestFiles.Count

if ($TotalTests -eq 0) {
    Write-Host "Error: No test files found in $TestCasesDir" -ForegroundColor Red
    exit 1
}

$HasAnswers = Test-Path $ExpectedDir

# --- Header ---
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Box Box Box - Test Runner                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Cases Found: " -NoNewline; Write-Host $TotalTests -ForegroundColor Yellow
Write-Host ""
Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host ""

$Passed = 0
$Failed = 0
$Errors = 0

foreach ($File in $TestFiles) {
    $TestName = $File.BaseName
    $TestId   = $TestName -replace "^test_", "TEST_"

    # Run the python script
    $outputJson = Get-Content $File.FullName | python solution/race_simulator.py | Out-String

    if ([string]::IsNullOrWhiteSpace($outputJson)) {
        Write-Host "✗ $TestId - Execution error (empty output)" -ForegroundColor Red
        $Errors++
        continue
    }

    # Validate JSON
    try {
        $parsed = ConvertFrom-Json $outputJson
    } catch {
        Write-Host "✗ $TestId - Invalid JSON output" -ForegroundColor Red
        $Failed++
        continue
    }

    $Predicted = $parsed.finishing_positions -join ","

    if ([string]::IsNullOrEmpty($Predicted) -or $Predicted -eq "null") {
        Write-Host "✗ $TestId - Invalid output format" -ForegroundColor Red
        $Failed++

    } elseif ($HasAnswers) {
        $AnswerFile = "$ExpectedDir/$TestName.json"
        if (Test-Path $AnswerFile) {
            $Expected = (Get-Content $AnswerFile | ConvertFrom-Json).finishing_positions -join ","
            if ($Predicted -eq $Expected) {
                Write-Host "✓ $TestId" -ForegroundColor Green
                $Passed++
            } else {
                Write-Host "✗ $TestId - Incorrect prediction" -ForegroundColor Red
                $Failed++
            }
        } else {
            Write-Host "? $TestId - Output generated (no answer file found)" -ForegroundColor Yellow
            $Passed++
        }

    } else {
        Write-Host "? $TestId - Output generated (no answer key to verify)" -ForegroundColor Yellow
        $Passed++
    }
}

# --- Results ---
$PassRate = if ($TotalTests -gt 0) { [math]::Round(($Passed / $TotalTests) * 100, 1) } else { 0 }

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Results                             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Tests:    " -NoNewline; Write-Host $TotalTests -ForegroundColor Yellow
Write-Host "Passed:         " -NoNewline; Write-Host $Passed     -ForegroundColor Green
Write-Host "Failed:         " -NoNewline; Write-Host $Failed     -ForegroundColor Red
if ($Errors -gt 0) {
    Write-Host "Errors:         " -NoNewline; Write-Host $Errors -ForegroundColor Red
}
Write-Host ""
Write-Host "Pass Rate:      " -NoNewline; Write-Host "$PassRate%" -ForegroundColor Green
Write-Host ""

if (-not $HasAnswers) {
    Write-Host "Note: Running without expected outputs. Only checking output format." -ForegroundColor Yellow
    Write-Host ""
}

if ($Passed -eq $TotalTests) {
    Write-Host "🏆 Perfect score! All tests passed!" -ForegroundColor Green
    exit 0
} elseif ($Passed -gt 0) {
    Write-Host "Keep improving! Check failed test cases." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "No tests passed. Review your implementation." -ForegroundColor Red
    exit 1
}