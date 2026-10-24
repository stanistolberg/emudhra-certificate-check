# Entwickelt von Stanislav Stolberg. Explicit, selected Windows app updates.
#requires -Version 5.1
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param([Parameter(Mandatory)][ValidateNotNullOrEmpty()][string[]]$PackageId, [switch]$Apply)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'Emudhra.Windows.psm1') -Force
# Validate the complete request before allowing any update.
$plans = @($PackageId | Select-Object -Unique | ForEach-Object {
    [pscustomobject]@{ Id = $_; Arguments = @(Get-EmudhraUpdateArgument -PackageId $_) }
})
if (-not $Apply) {
    foreach ($plan in $plans) { Write-Output ('PLAN: winget ' + ($plan.Arguments -join ' ')) }
    Write-Output 'No changes. Add -Apply to update only the explicitly selected installed packages.'
    Write-Output 'Windows itself: Settings > Windows Update, or your organisation-managed update channel.'
    exit 0
}
if (-not (Test-EmudhraWindowsPlatform)) { [Console]::Error.WriteLine('Applying updates requires Windows.'); exit 2 }
$failed = $false
foreach ($plan in $plans) {
    if ($PSCmdlet.ShouldProcess($plan.Id, 'Upgrade installed application with winget')) {
        $winget = Get-Command winget.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1
        $nativeArguments = $plan.Arguments
        & $winget.Source @nativeArguments
        if ($LASTEXITCODE -ne 0) {
            Write-Warning ('winget returned {0} for {1}; inspect its message. No success is assumed.' -f $LASTEXITCODE, $plan.Id)
            $failed = $true
        }
    }
}
Write-Output 'Rerun Test-Emudhra.ps1 after successful updates. Independent Python/Java CA bundles need separate maintenance.'
if ($failed) { exit 3 }
exit 0
