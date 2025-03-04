"use client";
import { useState } from "react";
import { open } from "@tauri-apps/plugin-dialog";

export default function FileSelector() {
  const [filePath, setFilePath] = useState("");

  const handleFileSelect = async () => {
    try {
      const selectedPath = await open({
        multiple: false, // 単一ファイル選択
      });

      if (selectedPath) {
        setFilePath(selectedPath);
      }
    } catch (error) {
      console.error("ファイル選択エラー:", error);
    }
  };

  return (
    <div>
      <h1>Tauri 2 - ファイル選択</h1>
      <button onClick={handleFileSelect}>ファイルを選択</button>
      {filePath && <p>選択されたファイル: {filePath}</p>}
    </div>
  );
}



$sourcePath = "C:\LocalFolder"  # 移動元フォルダ
$destinationPath = "\\ServerName\Share\"  # 移動先（共有フォルダ）

while ((Get-ChildItem -Path $sourcePath -Directory).Count -gt 0) {
    # 最初のフォルダを取得
    $folder = Get-ChildItem -Path $sourcePath -Directory | Select-Object -First 1
    if ($folder) {
        $sourceFolderPath = $folder.FullName
        $destFolderPath = Join-Path -Path $destinationPath -ChildPath $folder.Name
        
        try {
            # フォルダを移動
            Move-Item -Path $sourceFolderPath -Destination $destFolderPath -Force
            Write-Host "Moved: $sourceFolderPath -> $destFolderPath"
        }
        catch {
            Write-Host "Failed to move: $sourceFolderPath" -ForegroundColor Red
        }
    }
}
Write-Host "All folders moved successfully!"