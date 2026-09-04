# Helper script to connect this local Git repo to GitHub and push
param (
    [Parameter(Mandatory=$false)]
    [string]$RepoUrl
)

$gitExe = "C:\Program Files\Git\cmd\git.exe"

if (-not $RepoUrl) {
    $RepoUrl = Read-Host "Enter your GitHub repository URL (e.g. https://github.com/username/mechsuite.git)"
}

if (-not $RepoUrl) {
    Write-Host "No repository URL provided. Exiting." -ForegroundColor Yellow
    exit 1
}

Write-Host "Configuring remote origin: $RepoUrl" -ForegroundColor Cyan
& $gitExe remote remove origin 2>$null
& $gitExe remote add origin $RepoUrl

Write-Host "Pushing main branch to GitHub..." -ForegroundColor Cyan
& $gitExe branch -M main
& $gitExe push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSUCCESS! Your project is now pushed to GitHub." -ForegroundColor Green
    Write-Host "Next step: Go to https://railway.app -> New Project -> Deploy from GitHub repo!" -ForegroundColor Yellow
} else {
    Write-Host "`nPush encountered an issue. Please verify your repository URL and credentials." -ForegroundColor Red
}
