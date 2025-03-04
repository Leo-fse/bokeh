$sourcePath = "C:\LocalFolder"
$destinationPath = "\\ServerName\Share\"
$logFile = "C:\LocalFolder\move-log.txt"

while ((Get-ChildItem -Path $sourcePath -Directory).Count -gt 0) {
    $folder = Get-ChildItem -Path $sourcePath -Directory | Select-Object -First 1
    if ($folder) {
        $sourceFolderPath = $folder.FullName
        $zipFilePath = "$sourceFolderPath.zip"

        # 空のフォルダなら削除
        if ((Get-ChildItem -Path $sourceFolderPath -Recurse -Force).Count -eq 0) {
            Write-Host "Skipping empty folder: $sourceFolderPath"
            Remove-Item -Path $sourceFolderPath -Recurse -Force
            Add-Content -Path $logFile -Value "Skipped empty folder: $sourceFolderPath"
            continue
        }

        # 圧縮前に 0KB のファイルを削除
        Get-ChildItem -Path $sourceFolderPath -File | Where-Object { $_.Length -eq 0 } | Remove-Item -Force

        # 圧縮処理
        try {
            Write-Host "Compressing: $sourceFolderPath -> $zipFilePath"
            Compress-Archive -Path $sourceFolderPath -DestinationPath $zipFilePath -Force
            Remove-Item -Path $sourceFolderPath -Recurse -Force
            Add-Content -Path $logFile -Value "Compressed: $sourceFolderPath -> $zipFilePath"
        }
        catch {
            Write-Host "Failed to compress: $sourceFolderPath" -ForegroundColor Red
            Add-Content -Path $logFile -Value "Failed to compress: $sourceFolderPath - Error: $_"
            continue
        }

        # ZIPを移動
        $destZipPath = Join-Path -Path $destinationPath -ChildPath (Split-Path -Leaf $zipFilePath)
        try {
            Move-Item -Path $zipFilePath -Destination $destZipPath -Force
            Write-Host "Moved: $zipFilePath -> $destZipPath"
            Add-Content -Path $logFile -Value "Moved: $zipFilePath -> $destZipPath"
        }
        catch {
            Write-Host "Failed to move: $zipFilePath" -ForegroundColor Red
            Add-Content -Path $logFile -Value "Failed to move: $zipFilePath - Error: $_"
        }
    }
}

Write-Host "All folders processed successfully!"