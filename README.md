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