function BackupPutty {
    param ()

    Write-Host "Backing up Putty from the registry"
    $puttyBackupFilepath = 'Z:\Device & App Backups\copper\AppData\Putty\putty.reg'
    $puttyBackupTempFilepath = "D:\Temp\putty.reg"

    if (Test-Path $puttyBackupTempFilepath) {
        Remove-Item $puttyBackupTempFilepath -Force
    }

    reg export "HKEY_CURRENT_USER\Software\SimonTatham" $puttyBackupTempFilepath

    if (Test-Path $puttyBackupFilepath) {
        $existingBackupChecksum = (Get-FileHash $puttyBackupFilepath -Algorithm SHA256).Hash
        $newBackupChecksum = (Get-FileHash $puttyBackupTempFilepath -Algorithm SHA256).Hash
        $skipBackup = $false

        if ($existingBackupChecksum -eq $newBackupChecksum) {
            Write-Host "Skipping backup of putty registry keys: no changes since the existing backup"
            $skipBackup = $true

        } else {
            Write-Host "Putty registry settings changed since last backup: removing old backup file"
            Remove-Item $puttyBackupFilepath
        }
    }

    if (-not $skipBackup) {
        Write-Host "Making backup of registry entries for Putty"
        Copy-Item $puttyBackupTempFilepath -Destination $puttyBackupFilepath 
    }

    Remove-Item $puttyBackupTempFilepath -Force
}


Write-Host "Prefbak Init Script: starting script"
BackupPutty

Write-Host "Prefbak Init Script: complete"
