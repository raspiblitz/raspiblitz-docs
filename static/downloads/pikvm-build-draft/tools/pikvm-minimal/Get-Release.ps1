<#
.SYNOPSIS
Build on the PiKVM and collect the verified unsigned archive, or collect an existing run.
.EXAMPLE
./Get-Release.ps1 -Build fatpack
.EXAMPLE
./Get-Release.ps1 -Destination D:\Releases
.EXAMPLE
./Get-Release.ps1 -RunId 20261126T143254Z-01d2995d
#>
[CmdletBinding(DefaultParameterSetName = 'Pickup')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Build')]
    [ValidateSet('minimal', 'fatpack')]
    [string] $Build,

    [Parameter(ParameterSetName = 'Pickup')]
    [ValidatePattern('\A[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}\z')]
    [string] $RunId,

    [string] $Destination = (Join-Path (Join-Path $HOME 'Downloads') 'RaspiBlitz'),

    [ValidatePattern('\A[a-zA-Z0-9][a-zA-Z0-9.-]*\z')]
    [string] $PiKvm = 'pikvm-release'
)

$ErrorActionPreference = 'Stop'
$sshOptions = @('-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                '-o', 'ConnectTimeout=15', '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3')
$stateDir = '/var/lib/kvmd/msd/raspiblitz-image-build'
$controller = "/usr/bin/python $stateDir/controller/tools/pikvm-minimal/build.py"
$destinationDir = [IO.Directory]::CreateDirectory(
    $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination)).FullName

if ($Build) {
    $Build = $Build.ToLowerInvariant()
    $RunId = [datetime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
    $unit = "rb-release-$RunId"
    Write-Host "PiKVM build $Build ($RunId). Log: ssh $PiKvm journalctl -fu $unit"
    Write-Host "After a workstation disconnect, collect this run with -RunId $RunId."
    # The controller and its journal belong to the PiKVM service manager, independent of this SSH client.
    ssh @sshOptions $PiKvm "$controller start --wait --variant $Build --run-id $RunId" | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw ("PiKVM build or connection failed. Check: ssh $PiKvm journalctl -u $unit. " +
               "Guest log: ssh $PiKvm tail -n 50 $stateDir/$RunId/guest.log")
    }
} elseif (-not $RunId) {
    $runs = @(ssh @sshOptions $PiKvm "$controller list")
    if ($LASTEXITCODE -ne 0) { throw 'Could not list PiKVM builds.' }
    $ready = @(foreach ($line in $runs) {
        if ($line -cmatch '^([0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}) exported$') { $Matches[1] }
    })
    if ($ready.Count -eq 0) { throw 'No completed export is waiting on the PiKVM.' }
    if ($ready.Count -gt 1) { throw "Select a completed export with -RunId. Available: $($ready -join ', ')" }
    $RunId = $ready[0]
}

$remoteRun = "$stateDir/$RunId/export"
$releaseDir = Join-Path $destinationDir $RunId
$stagingDir = Join-Path $destinationDir ".download-$RunId"

function Read-Manifest([string] $Directory) {
    $report = Get-Content -Raw -LiteralPath (Join-Path $Directory 'build.json') | ConvertFrom-Json
    if ($report.run -cne $RunId -or
        $report.archive -cnotmatch '\Araspiblitz-(min|fat)-v[0-9][a-zA-Z0-9.-]+\.img\.gz\z' -or
        $report.archive_sha256 -cnotmatch '\A[a-f0-9]{64}\z' -or $report.raw_sha256 -cnotmatch '\A[a-f0-9]{64}\z' -or
        [long]$report.archive_bytes -le 0 -or [long]$report.raw_bytes -le 0 -or $report.test_boot_nvme_isolated -ne $true) {
        throw 'Unexpected release manifest.'
    }
    $variant = if ($report.archive.StartsWith('raspiblitz-fat-')) { 'fatpack' } else { 'minimal' }
    # Minimal exports created before variant support did not record the variant.
    if (($report.variant -cne $variant -and ($report.variant -or $variant -ne 'minimal')) -or ($Build -and $Build -ne $variant)) {
        throw 'Requested variant, manifest and archive name disagree.'
    }
    if ($variant -eq 'fatpack') {
        $minimum = [long]$report.fatpack_root_free_bytes
        $web = $report.fatpack_web_probe
        if ($minimum -le 0 -or [long]$report.fatpack_root_cold_available_bytes -lt $minimum -or
            [long]$report.fatpack_root_boot_available_bytes -lt $minimum -or
            $web.index_sha256 -cnotmatch '\A[a-f0-9]{64}\z' -or
            "$($web.setup_state)/$($web.setup_phase)" -cnotin @('noHDD/boot', 'waitsetup/setup')) {
            throw 'Fatpack has no passing root-space and setup-API evidence. It cannot be collected for signing.'
        }
    }
    return $report
}

function Receive-Files([string[]] $Commands) {
    Push-Location -LiteralPath $stagingDir
    try {
        $Commands | sftp @sshOptions -b - $PiKvm | Out-Host
        if ($LASTEXITCODE -ne 0) { throw "Transfer interrupted. Repeat with -RunId $RunId and the same destination to resume." }
    } finally {
        Pop-Location
    }
}

function Confirm-Release([string] $Directory, $Report) {
    $archive = Join-Path $Directory $Report.archive
    $rawName = [IO.Path]::GetFileNameWithoutExtension($Report.archive)
    foreach ($entry in @(@($Report.archive, $Report.archive_sha256), @($rawName, $Report.raw_sha256))) {
        $sidecar = Join-Path $Directory ($entry[0] + '.sha256')
        if ((Get-Content -Raw -LiteralPath $sidecar).TrimEnd() -cne "$($entry[1])  $($entry[0])") {
            throw "Checksum file disagrees with build.json: $sidecar"
        }
    }
    if ((Get-Item -LiteralPath $archive).Length -ne $Report.archive_bytes -or
        (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -cne $Report.archive_sha256) {
        if ($Directory -eq $stagingDir) {
            # A bad prefix cannot be repaired by SFTP resume. Retry from byte zero.
            [IO.File]::Delete($archive)
        }
        throw "Local archive verification failed. The PiKVM export is retained. Retry with -RunId $RunId."
    }
}

# Two calls from the same workstation must never append to the same partial archive.
$lock = [IO.FileStream]::new((Join-Path $destinationDir ".pickup-$RunId.lock"), [IO.FileMode]::OpenOrCreate,
                        [IO.FileAccess]::ReadWrite, [IO.FileShare]::None, 4096, [IO.FileOptions]::DeleteOnClose)
try {
    if ([IO.Directory]::Exists($releaseDir)) {
        $report = Read-Manifest $releaseDir
        Confirm-Release $releaseDir $report
    } else {
        $null = [IO.Directory]::CreateDirectory($stagingDir)
        try {
            Receive-Files @("get $remoteRun/build.json build.json")
        } catch {
            $transferError = $_
            try {
                $states = @(ssh @sshOptions $PiKvm "$controller list")
                $listed = $LASTEXITCODE -eq 0
            } catch { $listed = $false }
            if ($listed) {
                $entry = $states -cmatch "^$RunId "
                switch -CaseSensitive ($entry) {
                    "$RunId downloaded" { throw "Run $RunId was already collected. Use the original local destination or copy its verified archive." }
                    "$RunId preparing" { throw "Run $RunId is preparing. Check its PiKVM journal and collect after it reaches exported." }
                    "$RunId media-reserved" { throw "Run $RunId still holds its build media. Check its PiKVM journal and status before pickup." }
                    "$RunId failed-detached" { throw "Run $RunId failed. It produced no approved export." }
                    "$RunId abort-tested" { throw "Run $RunId was an abort test. There is no release archive to collect." }
                }
                if (-not $entry) { throw "Unknown run $RunId on $PiKvm. Check the PiKVM run list." }
            }
            throw $transferError
        }
        $report = Read-Manifest $stagingDir
        $name = $report.archive
        $rawName = [IO.Path]::GetFileNameWithoutExtension($name)
        $partial = Join-Path $stagingDir $name
        $received = if ([IO.File]::Exists($partial)) { (Get-Item -LiteralPath $partial).Length } else { 0 }
        if ($received -gt $report.archive_bytes) {
            [IO.File]::Delete($partial)
            $received = 0
        }
        $drive = (Get-Item -LiteralPath $stagingDir).PSDrive
        $remaining = [long]$report.archive_bytes - $received
        if ($null -ne $drive.Free -and $drive.Free -lt $remaining) {
            throw "Destination needs $remaining more bytes for the archive. Available: $($drive.Free)."
        }
        $commands = @("get $remoteRun/$name.sha256 $name.sha256", "get $remoteRun/$rawName.sha256 $rawName.sha256")
        if ($remaining -gt 0) {
            Write-Host "Downloading $name ($remaining bytes remaining) to $destinationDir"
            $action = if ($received -gt 0) { 'reget' } else { 'get' }
            $commands += "$action $remoteRun/$name $name"
        }
        Receive-Files $commands
        Confirm-Release $stagingDir $report
        [IO.Directory]::Move($stagingDir, $releaseDir)
    }

    ssh @sshOptions $PiKvm "$controller ack $RunId $($report.archive_sha256)" | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "Local archive verified at $releaseDir. Repeat with -RunId $RunId to acknowledge pickup." }
    $localArchive = Join-Path $releaseDir $report.archive
    Write-Host "Verified archive for manual signing: $localArchive"
    Write-Host "SHA-256 $($report.archive_sha256)"
    Get-Item -LiteralPath $localArchive
} finally {
    $lock.Dispose()
}
