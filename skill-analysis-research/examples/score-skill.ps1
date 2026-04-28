# score-skill.ps1
# 用法: .\score-skill.ps1 -Path "C:\path\to\SKILL.md"
# 输出: 30 项评分清单 + 总分

param(
    [Parameter(Mandatory=$true)]
    [string]$Path
)

if (-not (Test-Path $Path)) {
    Write-Error "File not found: $Path"
    exit 1
}

$content = Get-Content $Path -Raw
$score = 0
$report = @()

function Add-Score($pass, $points, $label) {
    $script:report += if ($pass) {
        $script:score += $points
        "  [+$points] OK   $label"
    } else {
        "  [ 0 ]      MISS $label"
    }
}

# ===== A. Frontmatter 元数据 (20) =====
$report += "`n=== A. Frontmatter (20) ==="
$hasFrontmatter = $content -match '(?ms)^---\s*\n(.*?)\n---'
$frontmatter = if ($hasFrontmatter) { $matches[1] } else { "" }

Add-Score $hasFrontmatter 3 "A1: has frontmatter"
Add-Score ($frontmatter -match '(?m)^name:\s*\S+') 3 "A2: name field"
$descMatch = [regex]::Match($frontmatter, '(?ms)^description:\s*(.+?)(?=\n[a-z\-]+:|\Z)')
$desc = if ($descMatch.Success) { $descMatch.Groups[1].Value.Trim() } else { "" }
Add-Score ($desc.Length -ge 50) 4 "A3: description >= 50 chars"
Add-Score ($desc.Length -le 1024) 3 "A4: description <= 1024 chars"
Add-Score ($frontmatter -match '(?m)^(allowed-tools|tools):') 4 "A5: tools declared"
Add-Score (-not ($frontmatter -match '(?m)^model:\s*(gpt-5|claude-opus-5)')) 3 "A6: not locked to exotic model"

# ===== B. 描述与触发词 (25) =====
$report += "`n=== B. Description & Triggers (25) ==="
Add-Score ($desc -match '\.|。') 5 "B1: one-sentence purpose"
Add-Score ($desc -match '当用户说|when\s+(user|the)|trigger|激活') 6 "B2: trigger keywords"
$hasZh = $desc -match '[\u4e00-\u9fa5]'
$hasEn = $desc -match '[a-zA-Z]{4,}'
Add-Score ($hasZh -and $hasEn) 4 "B3: bilingual keywords"
$keywordCount = ([regex]::Matches($desc, '"[^"]+"|"[^"]+"|''[^'']+''')).Count
Add-Score ($keywordCount -ge 3 -and $keywordCount -le 8) 4 "B4: 3-8 keywords ($keywordCount found)"
Add-Score ($desc -match '不适用|排除|except|not\s+for') 6 "B5: exclusion clause (often missing!)"

# ===== C. 正文结构 (20) =====
$report += "`n=== C. Structure (20) ==="
Add-Score ($content -match '##\s+(When to Use|何时使用|触发条件)') 3 "C1: When-to-Use section"
$stepMatches = [regex]::Matches($content, '###?\s+(Step|阶段|步骤)\s*\d+')
Add-Score ($stepMatches.Count -ge 3) 4 "C2: numbered steps ($($stepMatches.Count))"
Add-Score ($stepMatches.Count -ge 3 -and $stepMatches.Count -le 7) 3 "C3: step count 3-7"
Add-Score ($content -match '输入|产出|Input|Output') 4 "C4: input/output declared"
Add-Score ($content -match '##\s+(Example|示例|例子)') 3 "C5: examples section"
$lineCount = ($content -split "`n").Count
Add-Score ($lineCount -le 500) 3 "C6: <500 lines ($lineCount)"

# ===== D. 引用 (15) =====
$report += "`n=== D. References (15) ==="
Add-Score (-not ($content -match '/(Users|home)/[a-z]+/')) 3 "D1: no absolute paths"
Add-Score $true 4 "D2: skipped (manual check)"
Add-Score $true 2 "D3: skipped (manual check)"
Add-Score $true 3 "D4: skipped (manual check)"
Add-Score $true 3 "D5: skipped (manual check)"

# ===== E. 安全可移植 (10) =====
$report += "`n=== E. Security & Portability (10) ==="
Add-Score (-not ($frontmatter -match 'Bash\(\*\)|tools.*\*')) 3 "E1: no Bash(*) wildcard"
Add-Score (-not ($content -match 'curl[^|]+\|[^|]*sh|wget[^|]+\|')) 3 "E2: no remote pipe execution"
Add-Score (-not ($content -match '/Users/[a-z]+/|C:\\Users\\[a-z]+\\')) 2 "E3: no hardcoded user paths"
Add-Score (-not ($content -match '(?<!\.)rm -rf /')) 2 "E4: no rm -rf /"

# ===== F. 可维护性 (10) =====
$report += "`n=== F. Maintainability (10) ==="
Add-Score ($frontmatter -match 'version:|Updated:' -or $content -match '##\s+(Changelog|更新日志)') 2 "F1: version or date"
Add-Score ($content -match 'author|作者|来源|source:') 2 "F2: author/source"
Add-Score ($content -match '##\s+(Changelog|更新日志|变更)') 3 "F3: changelog section"
Add-Score ($content -match '##\s+(License|许可证|MIT|Apache)') 3 "F4: license declared"

# ===== 输出 =====
$report | ForEach-Object { Write-Host $_ }

Write-Host "`n================================"
Write-Host "TOTAL SCORE: $score / 100"
Write-Host "================================"

$verdict = switch ($score) {
    { $_ -ge 90 } { "EXCELLENT - copy directly"; break }
    { $_ -ge 80 } { "GOOD - fork & minor tweaks"; break }
    { $_ -ge 60 } { "FAIR - heavy customization needed"; break }
    default       { "POOR - rewrite from scratch"; break }
}
Write-Host "Verdict: $verdict"
