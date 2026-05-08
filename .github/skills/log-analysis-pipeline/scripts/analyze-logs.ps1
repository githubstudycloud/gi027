param(
    [Parameter(Mandatory = $true)]
    [string[]]$InputFiles,
    [string]$OutputDir = "./reports/output",
    [string]$FieldMapPath,
    [string]$DimensionRulesPath
)

$ErrorActionPreference = "Stop"

function Get-DefaultFieldMap {
    return @{
        useCaseName = @("useCaseName", "caseName")
        issueCategory = @("issueCategory", "problemCategory")
        issueSubcategory = @("issueSubcategory", "problemSubcategory")
        rootCauseConclusion = @("rootCauseConclusion", "rootCause")
        keyEvidence = @("keyEvidence", "evidence")
        fixAction = @("fixAction", "repairAction")
        fixConclusion = @("fixConclusion", "repairConclusion")
        rerunConclusion = @("rerunConclusion", "rerunResult")
    }
}

function Normalize-Text([string]$Text) {
    if ([string]::IsNullOrWhiteSpace($Text)) { return "N/A" }
    $value = $Text.Trim()
    $value = [regex]::Replace($value, "\s+", " ")
    return $value
}

function Convert-ToHashtable($obj) {
    $hash = @{}
    if ($null -eq $obj) { return $hash }

    if ($obj -is [System.Collections.IDictionary]) {
        foreach ($key in $obj.Keys) {
            $hash[$key] = $obj[$key]
        }
        return $hash
    }

    foreach ($p in $obj.PSObject.Properties) {
        $hash[$p.Name] = $p.Value
    }
    return $hash
}

function Find-FieldValue($recordHash, [string[]]$aliases) {
    foreach ($alias in $aliases) {
        if ($recordHash.ContainsKey($alias)) {
            $v = $recordHash[$alias]
            if ($null -ne $v -and -not [string]::IsNullOrWhiteSpace([string]$v)) {
                return [string]$v
            }
        }
    }
    return "N/A"
}

function Parse-JsonFile([string]$path) {
    $raw = Get-Content -Path $path -Raw -Encoding UTF8
    $parsed = $raw | ConvertFrom-Json

    if ($parsed -is [System.Array]) {
        return ,$parsed
    }

    if ($parsed.PSObject.Properties.Name -contains "records") {
        return ,$parsed.records
    }
    if ($parsed.PSObject.Properties.Name -contains "items") {
        return ,$parsed.items
    }
    if ($parsed.PSObject.Properties.Name -contains "data") {
        if ($parsed.data -is [System.Array]) {
            return ,$parsed.data
        }
        return ,@($parsed.data)
    }

    return ,@($parsed)
}

function Parse-TxtFile([string]$path) {
    $raw = Get-Content -Path $path -Raw -Encoding UTF8
    $blocks = [regex]::Split($raw.Trim(), "(\r?\n){2,}") | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

    $records = @()
    foreach ($block in $blocks) {
        $lines = $block -split "\r?\n"
        $h = @{}
        foreach ($line in $lines) {
            if ($line -match "^\s*([^:]+)\s*[:]\s*(.*)$") {
                $key = $matches[1].Trim()
                $val = $matches[2].Trim()
                $h[$key] = $val
            }
        }
        if ($h.Count -gt 0) {
            $records += [PSCustomObject]$h
        }
    }
    return $records
}

function Load-FieldMap([string]$mapPath) {
    if ([string]::IsNullOrWhiteSpace($mapPath)) {
        return Get-DefaultFieldMap
    }

    if (-not (Test-Path $mapPath)) {
        throw "Field map file not found: $mapPath"
    }

    $obj = Get-Content -Path $mapPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($null -eq $obj.fields) {
        return Get-DefaultFieldMap
    }

    $map = @{}
    foreach ($p in $obj.fields.PSObject.Properties) {
        $arr = @()
        foreach ($item in $p.Value) { $arr += [string]$item }
        $map[$p.Name] = $arr
    }
    return $map
}

function Load-DimensionRules([string]$rulesPath) {
    $default = @("issueCategory", "issueSubcategory", "rootCauseConclusion")
    if ([string]::IsNullOrWhiteSpace($rulesPath)) {
        return $default
    }

    if (-not (Test-Path $rulesPath)) {
        throw "Dimension rules file not found: $rulesPath"
    }

    $obj = Get-Content -Path $rulesPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($null -eq $obj.groupBy -or $obj.groupBy.Count -eq 0) {
        return $default
    }

    $groupBy = @()
    foreach ($d in $obj.groupBy) { $groupBy += [string]$d }
    return $groupBy
}

function Normalize-Record($recordObj, $fieldMap, [string]$sourceFile) {
    $hash = Convert-ToHashtable $recordObj

    $normalized = [ordered]@{}
    foreach ($canonical in $fieldMap.Keys) {
        $normalized[$canonical] = Normalize-Text (Find-FieldValue $hash $fieldMap[$canonical])
    }

    $normalized["sourceFile"] = $sourceFile
    return [PSCustomObject]$normalized
}

function Ensure-OutputDir([string]$path) {
    if (-not (Test-Path $path)) {
        New-Item -Path $path -ItemType Directory -Force | Out-Null
    }
}

function Build-GroupKey($record, [string[]]$groupBy) {
    $parts = @()
    foreach ($g in $groupBy) {
        $parts += [string]($record.$g)
    }
    return $parts -join "||"
}

$fieldMap = Load-FieldMap $FieldMapPath
$groupBy = Load-DimensionRules $DimensionRulesPath

$resolvedFiles = @()
foreach ($file in $InputFiles) {
    if (Test-Path $file) {
        $resolvedFiles += (Resolve-Path $file).Path
    }
}

if ($resolvedFiles.Count -eq 0) {
    throw "No supported input files were found."
}

$allRecords = @()
foreach ($file in $resolvedFiles) {
    $ext = [System.IO.Path]::GetExtension($file).ToLowerInvariant()
    $records = @()

    if ($ext -eq ".json") {
        $records = Parse-JsonFile $file
    } elseif ($ext -eq ".txt") {
        $records = Parse-TxtFile $file
    } else {
        continue
    }

    foreach ($r in $records) {
        $allRecords += (Normalize-Record -recordObj $r -fieldMap $fieldMap -sourceFile $file)
    }
}

if ($allRecords.Count -eq 0) {
    throw "No valid records were parsed from input files."
}

$groups = @{}
foreach ($rec in $allRecords) {
    $key = Build-GroupKey $rec $groupBy
    if (-not $groups.ContainsKey($key)) {
        $groups[$key] = New-Object System.Collections.ArrayList
    }
    [void]$groups[$key].Add($rec)
}

Ensure-OutputDir $OutputDir

$normalizedPath = Join-Path $OutputDir "normalized-records.json"
$summaryPath = Join-Path $OutputDir "summary.json"
$reportPath = Join-Path $OutputDir "log-analysis-report.md"

$allRecords | ConvertTo-Json -Depth 100 | Out-File -FilePath $normalizedPath -Encoding utf8

$summaryObject = [ordered]@{
    generatedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    totalFiles = $resolvedFiles.Count
    totalRecords = $allRecords.Count
    totalGroups = $groups.Keys.Count
    groupBy = $groupBy
    files = $resolvedFiles
}
$summaryObject | ConvertTo-Json -Depth 100 | Out-File -FilePath $summaryPath -Encoding utf8

$lines = New-Object System.Collections.ArrayList
[void]$lines.Add("# Log Analysis Summary Report")
[void]$lines.Add("")
[void]$lines.Add("## Overview")
[void]$lines.Add("")
[void]$lines.Add("| Metric | Value |")
[void]$lines.Add("|---|---|")
[void]$lines.Add("| Input files | $($resolvedFiles.Count) |")
[void]$lines.Add("| Total records | $($allRecords.Count) |")
[void]$lines.Add("| Total groups | $($groups.Keys.Count) |")
[void]$lines.Add("")

[void]$lines.Add("## Category Summary")
[void]$lines.Add("")
[void]$lines.Add("| Issue Category | Issue Subcategory | Root Cause | Count |")
[void]$lines.Add("|---|---|---|---:|")

$sortedKeys = $groups.Keys | Sort-Object {
    -1 * $groups[$_].Count
}

foreach ($key in $sortedKeys) {
    $first = $groups[$key][0]
    [void]$lines.Add("| $($first.issueCategory) | $($first.issueSubcategory) | $($first.rootCauseConclusion) | $($groups[$key].Count) |")
}

[void]$lines.Add("")
[void]$lines.Add("## Nested Details")
[void]$lines.Add("")

$index = 1
foreach ($key in $sortedKeys) {
    $first = $groups[$key][0]
    [void]$lines.Add("### $index. $($first.issueCategory) / $($first.issueSubcategory) / $($first.rootCauseConclusion)")
    [void]$lines.Add("")
    [void]$lines.Add("| Use Case | Key Evidence | Fix Action | Fix Conclusion | Rerun Conclusion | Source File |")
    [void]$lines.Add("|---|---|---|---|---|---|")
    foreach ($rec in $groups[$key]) {
        [void]$lines.Add("| $($rec.useCaseName) | $($rec.keyEvidence) | $($rec.fixAction) | $($rec.fixConclusion) | $($rec.rerunConclusion) | $([System.IO.Path]::GetFileName($rec.sourceFile)) |")
    }
    [void]$lines.Add("")
    $index++
}

$lines -join "`r`n" | Out-File -FilePath $reportPath -Encoding utf8

Write-Host "Analysis completed."
Write-Host "- Report: $reportPath"
Write-Host "- Records: $normalizedPath"
Write-Host "- Summary: $summaryPath"
