# convert-skill.ps1
# 用法: .\convert-skill.ps1 -Source <SKILL.md> -Target <claude|copilot|opencode|cursor> -OutDir <dir>
# 作用: 把 SKILL.md 在不同工具格式间转换 frontmatter

param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][ValidateSet("claude","copilot","opencode","cursor")][string]$Target,
    [Parameter(Mandatory=$true)][string]$OutDir
)

if (-not (Test-Path $Source)) { Write-Error "Source not found"; exit 1 }
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

$content = Get-Content $Source -Raw
$m = [regex]::Match($content, '(?ms)^---\s*\n(.*?)\n---\s*\n(.*)$')
if (-not $m.Success) { Write-Error "No frontmatter found"; exit 1 }

$fm = $m.Groups[1].Value
$body = $m.Groups[2].Value

# 解析 frontmatter 成字典
$fmDict = @{}
foreach ($line in ($fm -split "`n")) {
    if ($line -match '^([a-zA-Z\-]+):\s*(.*)$') {
        $fmDict[$matches[1]] = $matches[2].Trim()
    }
}

$newFm = @{}

switch ($Target) {
    "claude" {
        # 复制兼容字段
        foreach ($k in @("name","description","allowed-tools","model","argument-hint")) {
            if ($fmDict.ContainsKey($k)) { $newFm[$k] = $fmDict[$k] }
        }
    }
    "copilot" {
        if ($fmDict.ContainsKey("description")) { $newFm["description"] = $fmDict["description"] }
        $newFm["applyTo"] = '"**"'
        # tools 字段（可选）
        if ($fmDict.ContainsKey("allowed-tools")) {
            $tools = $fmDict["allowed-tools"] -replace 'Bash\([^)]+\)', 'run_in_terminal'
            $newFm["# tools (optional)"] = "[$tools]"
        }
    }
    "opencode" {
        if ($fmDict.ContainsKey("description")) { $newFm["description"] = $fmDict["description"] }
        $newFm["mode"] = "subagent"
        if ($fmDict.ContainsKey("allowed-tools")) {
            $newFm["# tools"] = "{ read: true, write: true, bash: false }"
        }
    }
    "cursor" {
        if ($fmDict.ContainsKey("description")) {
            $d = $fmDict["description"]
            if ($d.Length -gt 200) { $d = $d.Substring(0,197) + "..." }
            $newFm["description"] = $d
        }
        $newFm["globs"] = '["**/*"]'
        $newFm["alwaysApply"] = "false"
    }
}

# 输出
$outFm = ($newFm.GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value)" }) -join "`n"
$header = "---`n$outFm`n---`n"
$migrationNote = @"

> Migration note: converted from $(Split-Path $Source -Leaf) to $Target format
> Date: $(Get-Date -Format "yyyy-MM-dd")
> ⚠️ Manually review frontmatter and any tool-specific syntax in body
"@

$result = $header + $migrationNote + "`n" + $body
$outName = [System.IO.Path]::GetFileNameWithoutExtension($Source) + "-$Target.md"
$outPath = Join-Path $OutDir $outName
Set-Content -Path $outPath -Value $result -Encoding UTF8

Write-Host "Converted: $outPath"
Write-Host "Frontmatter changed:"
$newFm.GetEnumerator() | ForEach-Object { Write-Host "  $($_.Key): $($_.Value)" }
Write-Host "`n⚠️  Please manually review the output before using."
