param(
    [string]$OutputDir = "./tests/fixtures"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
}

$jsonData = @(
    @{
        useCaseName = "Login retry timeout"
        issueCategory = "Stability"
        issueSubcategory = "Timeout"
        rootCauseConclusion = "Slow downstream service"
        keyEvidence = "P95 latency is 4.2s"
        fixAction = "Add timeout and retry policy"
        fixConclusion = "Mitigated"
        rerunConclusion = "Passed"
    },
    @{
        caseName = "Payment callback signature mismatch"
        problemCategory = "Correctness"
        problemSubcategory = "Signature"
        rootCause = "Key version mismatch"
        evidence = "Gateway and service use different key versions"
        repairAction = "Align key versions"
        repairConclusion = "Fixed"
        rerunResult = "Passed"
    }
)

$txtData = @"
useCaseName: Order query intermittent failure
issueCategory: Stability
issueSubcategory: Network
rootCauseConclusion: Network jitter
keyEvidence: 3 connection resets
fixAction: Enable keepalive in connection pool
fixConclusion: Fixed
rerunConclusion: Passed

useCaseName: Profile update missing fields
issueCategory: DataConsistency
issueSubcategory: Mapping
rootCauseConclusion: Missing DTO mapping
keyEvidence: Trace comparison shows field not propagated
fixAction: Add missing mapping and regression tests
fixConclusion: Fixed
rerunConclusion: Passed
"@

$jsonPath = Join-Path $OutputDir "sample-input-1.json"
$txtPath = Join-Path $OutputDir "sample-input-2.txt"

$jsonData | ConvertTo-Json -Depth 100 | Out-File -FilePath $jsonPath -Encoding utf8
$txtData | Out-File -FilePath $txtPath -Encoding utf8

Write-Host "Test fixtures generated:"
Write-Host "- $jsonPath"
Write-Host "- $txtPath"
