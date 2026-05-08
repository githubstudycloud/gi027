param(
    [string]$SkillRoot = ".",
    [string]$Version = "v1.0.0"
)

$ErrorActionPreference = "Stop"

$skillRootPath = (Resolve-Path $SkillRoot).Path
$scriptsDir = Join-Path $skillRootPath "scripts"
$assetsDir = Join-Path $skillRootPath "assets"
$fixturesDir = Join-Path $skillRootPath "tests/fixtures"
$outputDir = Join-Path $skillRootPath "reports/output"
$reportPath = Join-Path $skillRootPath "reports/test-report.md"

$testResults = New-Object System.Collections.ArrayList

function Add-Result([string]$name, [bool]$passed, [string]$detail) {
    [void]$testResults.Add([PSCustomObject]@{
        Name = $name
        Passed = $passed
        Detail = $detail
    })
}

try {
    & (Join-Path $scriptsDir "generate-test-data.ps1") -OutputDir $fixturesDir | Out-Null
    Add-Result -name "Generate fixtures" -passed $true -detail "JSON/TXT fixtures generated"
} catch {
    Add-Result -name "Generate fixtures" -passed $false -detail $_.Exception.Message
}

try {
    $inputs = @(
        (Join-Path $fixturesDir "sample-input-1.json"),
        (Join-Path $fixturesDir "sample-input-2.txt")
    )

    & (Join-Path $scriptsDir "analyze-logs.ps1") `
        -InputFiles $inputs `
        -OutputDir $outputDir `
        -FieldMapPath (Join-Path $assetsDir "field-map.example.json") `
        -DimensionRulesPath (Join-Path $assetsDir "dimension-rules.example.json") | Out-Null

    Add-Result -name "Run log analysis" -passed $true -detail "Analysis pipeline succeeded"
} catch {
    Add-Result -name "Run log analysis" -passed $false -detail $_.Exception.Message
}

$reportFile = Join-Path $outputDir "log-analysis-report.md"
$summaryFile = Join-Path $outputDir "summary.json"
$normalizedFile = Join-Path $outputDir "normalized-records.json"

Add-Result -name "Report exists" -passed (Test-Path $reportFile) -detail $reportFile
Add-Result -name "Summary exists" -passed (Test-Path $summaryFile) -detail $summaryFile
Add-Result -name "Normalized JSON exists" -passed (Test-Path $normalizedFile) -detail $normalizedFile

if (Test-Path $reportFile) {
    $content = Get-Content -Path $reportFile -Raw -Encoding UTF8
    Add-Result -name "Report has category summary section" -passed ($content.Contains("## Category Summary")) -detail "Main table heading check"
    Add-Result -name "Report has nested details section" -passed ($content.Contains("## Nested Details")) -detail "Nested details heading check"
}

$passedCount = ($testResults | Where-Object { $_.Passed }).Count
$totalCount = $testResults.Count
$allPassed = ($passedCount -eq $totalCount)

$resultText = if ($allPassed) { "PASS" } else { "FAIL" }

$lines = New-Object System.Collections.ArrayList
[void]$lines.Add("# Log Analysis Skill Test Report")
[void]$lines.Add("")
[void]$lines.Add("- Version: $Version")
[void]$lines.Add("- GeneratedAt: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$lines.Add("- Result: $resultText")
[void]$lines.Add("")
[void]$lines.Add("## Test Details")
[void]$lines.Add("")
[void]$lines.Add("| Case | Result | Detail |")
[void]$lines.Add("|---|---|---|")

foreach ($result in $testResults) {
    $status = if ($result.Passed) { "PASS" } else { "FAIL" }
    [void]$lines.Add("| $($result.Name) | $status | $($result.Detail) |")
}

[void]$lines.Add("")
[void]$lines.Add("## Conclusion")
[void]$lines.Add("")
if ($allPassed) {
    [void]$lines.Add("Ready for formal release: commit, push, and tag.")
} else {
    [void]$lines.Add("Fix failed checks before release.")
}

if (-not (Test-Path (Split-Path $reportPath -Parent))) {
    New-Item -Path (Split-Path $reportPath -Parent) -ItemType Directory -Force | Out-Null
}

$lines -join "`r`n" | Out-File -FilePath $reportPath -Encoding utf8

Write-Host "Test report generated: $reportPath"

if (-not $allPassed) {
    exit 1
}
