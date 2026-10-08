<#
.SYNOPSIS
    指定された別リポジトリと現在のリポジトリ間で AI ハーネス設定の差分および新旧関係を一覧表示します。

.PARAMETER SourceRepo
    同期元（比較対象）のリポジトリパス（例: "e:\work\IntervalTimer" または "../IntervalTimer"）
#>
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$SourceRepo
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SourceRepo)) {
    Write-Error "Repository path not found: $SourceRepo"
    exit 1
}

$SourceRepo = (Resolve-Path $SourceRepo).Path
$CurrentRepo = (Get-Location).Path

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " AI Harness Diff & Freshness Scanner" -ForegroundColor Cyan
Write-Host " Source (Remote) : $SourceRepo"
Write-Host " Target (Local)  : $CurrentRepo"
Write-Host "==========================================================" -ForegroundColor Cyan

function Get-GitCommitDate {
    param([string]$RepoPath, [string]$RelativePath)
    try {
        $dateStr = & git -C "$RepoPath" log -1 --format="%ci" -- "$RelativePath" 2>$null
        if ($dateStr -and -not [string]::IsNullOrWhiteSpace($dateStr)) {
            return [DateTime]::Parse($dateStr.Trim())
        }
    } catch {
        # ignore
    }
    $fullPath = Join-Path $RepoPath $RelativePath
    if (Test-Path $fullPath) {
        return (Get-Item $fullPath).LastWriteTime
    }
    return $null
}

# 比較対象の個別ファイル・設定一覧を収集
$fixedTargets = @(
    "AGENTS.md",
    "docs/issues/TEMPLATE.md",
    ".github/pull_request_template.md",
    ".githooks/pre-commit",
    ".githooks/pre-push"
)

# .agents/ 配下のファイルを動的に収集（Source と Target の両方からユニーク化）
$agentFiles = [System.Collections.Generic.HashSet[string]]::new()
foreach ($base in @($SourceRepo, $CurrentRepo)) {
    $agentsDir = Join-Path $base ".agents"
    if (Test-Path $agentsDir) {
        Get-ChildItem -Path $agentsDir -Recurse -File | ForEach-Object {
            $rel = [System.IO.Path]::GetRelativePath($base, $_.FullName).Replace("\", "/")
            $agentFiles.Add($rel) | Out-Null
        }
    }
}

$allTargets = @($fixedTargets) + @($agentFiles | Sort-Object)

$results = @()

foreach ($target in $allTargets) {
    $srcPath = Join-Path $SourceRepo $target
    $dstPath = Join-Path $CurrentRepo $target

    $srcExists = Test-Path $srcPath
    $dstExists = Test-Path $dstPath

    if (-not $srcExists -and -not $dstExists) {
        continue
    }

    $srcDate = if ($srcExists) { Get-GitCommitDate -RepoPath $SourceRepo -RelativePath $target } else { $null }
    $dstDate = if ($dstExists) { Get-GitCommitDate -RepoPath $CurrentRepo -RelativePath $target } else { $null }

    $srcDateStr = if ($srcDate) { $srcDate.ToString("yyyy-MM-dd HH:mm") } else { "-" }
    $dstDateStr = if ($dstDate) { $dstDate.ToString("yyyy-MM-dd HH:mm") } else { "-" }

    if ($srcExists -and -not $dstExists) {
        $results += [PSCustomObject]@{
            Target        = $target
            Status        = "Source Only"
            Newer         = "Source (New [CANDIDATE])"
            SourceUpdated = $srcDateStr
            TargetUpdated = $dstDateStr
        }
    } elseif (-not $srcExists -and $dstExists) {
        $results += [PSCustomObject]@{
            Target        = $target
            Status        = "Target Only"
            Newer         = "Target (Local)"
            SourceUpdated = $srcDateStr
            TargetUpdated = $dstDateStr
        }
    } else {
        # 両方存在する場合の diff 判定
        $diffOutput = & git diff --no-index --quiet "$dstPath" "$srcPath" 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            $results += [PSCustomObject]@{
                Target        = $target
                Status        = "Identical"
                Newer         = "Same"
                SourceUpdated = $srcDateStr
                TargetUpdated = $dstDateStr
            }
        } else {
            # 差分ありの場合の新旧判定
            $newer = "Unknown"
            if ($srcDate -and $dstDate) {
                if ($srcDate -gt $dstDate.AddMinutes(1)) {
                    $newer = "Source (Update [CANDIDATE])"
                } elseif ($dstDate -gt $srcDate.AddMinutes(1)) {
                    $newer = "Target (Newer [CAUTION])"
                } else {
                    $newer = "Same Time"
                }
            }

            $results += [PSCustomObject]@{
                Target        = $target
                Status        = "Different"
                Newer         = $newer
                SourceUpdated = $srcDateStr
                TargetUpdated = $dstDateStr
            }
        }
    }
}

$results | Format-Table -AutoSize

Write-Host "`n[Legend / Judge Details]:" -ForegroundColor Yellow
Write-Host "  Source (Update [CANDIDATE]) : Source repo is newer. Candidate for syncing into local."
Write-Host "  Target (Newer [CAUTION])    : Local target is newer! Risk of degradation if overwritten!"
Write-Host "  Identical                   : Exact match (no diff)."
Write-Host "  Source Only                 : Exists only in source repo (new feature candidate)."
Write-Host "  Target Only                 : Exists only in local repo."
Write-Host "`n[Detailed Diff Command]:" -ForegroundColor Yellow
Write-Host "  git diff --no-index <TargetFilePath> <SourceFilePath>`n"
