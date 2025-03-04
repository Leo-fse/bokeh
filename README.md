$sourcePath = "C:\LocalFolder"  # 移動元フォルダ
$destinationPath = "\\ServerName\Share\"  # 共有フォルダのパス
$logFile = "C:\LocalFolder\move-log.txt"  # ログファイル
$7zipPath = "C:\Program Files\7-Zip\7z.exe"  # 7-Zip のパス
$foldersToDelete = @("node_modules", ".venv", ".next")  # 削除対象のフォルダリスト

# 7-Zip がインストールされているか確認
if (!(Test-Path $7zipPath)) {
    Write-Host "Error: 7-Zip not found at $7zipPath" -ForegroundColor Red
    exit 1
}

while ((Get-ChildItem -Path $sourcePath -Directory).Count -gt 0) {
    $folder = Get-ChildItem -Path $sourcePath -Directory | Select-Object -First 1
    if ($folder) {
        $sourceFolderPath = $folder.FullName
        $zipFilePath = "$sourceFolderPath.zip"

        # サブディレクトリを含めて削除対象フォルダを検索して削除
        foreach ($delFolder in $foldersToDelete) {
            $delPaths = Get-ChildItem -Path $sourceFolderPath -Recurse -Directory -Force | Where-Object { $_.Name -eq $delFolder }
            foreach ($delPath in $delPaths) {
                if (Test-Path $delPath.FullName) {
                    try {
                        Write-Host "Deleting: $delPath"
                        Remove-Item -Path $delPath.FullName -Recurse -Force
                        Add-Content -Path $logFile -Value "Deleted: $delPath"
                    }
                    catch {
                        Write-Host "Failed to delete: $delPath" -ForegroundColor Red
                        Add-Content -Path $logFile -Value "Failed to delete: $delPath - Error: $_"
                    }
                }
            }
        }

        # 空のフォルダなら削除
        if ((Get-ChildItem -Path $sourceFolderPath -Recurse -Force).Count -eq 0) {
            Write-Host "Skipping empty folder: $sourceFolderPath"
            Remove-Item -Path $sourceFolderPath -Recurse -Force
            Add-Content -Path $logFile -Value "Skipped empty folder: $sourceFolderPath"
            continue
        }

        # 圧縮前に 0KB のファイルを削除
        Get-ChildItem -Path $sourceFolderPath -File -Recurse | Where-Object { $_.Length -eq 0 } | Remove-Item -Force

        # 圧縮処理（7-Zip を使用）
        try {
            Write-Host "Compressing with 7-Zip: $sourceFolderPath -> $zipFilePath"
            $arguments = "a -tzip `"$zipFilePath`" `"$sourceFolderPath\*`" -mx9"
            Start-Process -FilePath $7zipPath -ArgumentList $arguments -NoNewWindow -Wait
            Remove-Item -Path $sourceFolderPath -Recurse -Force  # 圧縮後に元フォルダを削除
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