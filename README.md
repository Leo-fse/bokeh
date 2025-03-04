$sourcePath = "C:\LocalFolder"  # 移動元フォルダ
$destinationPath = "\\ServerName\Share\"  # 移動先（共有フォルダ）
$logFile = "C:\LocalFolder\move-log.txt"  # ログファイル

# フォルダが空になるまで繰り返す
while ((Get-ChildItem -Path $sourcePath -Directory).Count -gt 0) {
    # 最初のフォルダを取得
    $folder = Get-ChildItem -Path $sourcePath -Directory | Select-Object -First 1
    if ($folder) {
        $sourceFolderPath = $folder.FullName
        $zipFilePath = "$sourceFolderPath.zip"

        # フォルダが未圧縮ならZIP化
        if (!(Test-Path $zipFilePath)) {
            try {
                Write-Host "Compressing: $sourceFolderPath -> $zipFilePath"
                Compress-Archive -Path $sourceFolderPath -DestinationPath $zipFilePath -Force
                Remove-Item -Path $sourceFolderPath -Recurse -Force  # 圧縮後に元フォルダを削除
                Add-Content -Path $logFile -Value "Compressed: $sourceFolderPath -> $zipFilePath"
            }
            catch {
                Write-Host "Failed to compress: $sourceFolderPath" -ForegroundColor Red
                Add-Content -Path $logFile -Value "Failed to compress: $sourceFolderPath - Error: $_"
                continue  # 次のフォルダに進む
            }
        }

        # 圧縮済みZIPファイルを移動
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