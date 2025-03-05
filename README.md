use duckdb::{Connection, Result};
use tauri::command;

#[command]
fn get_time_series_data() -> Result<Vec<String>, String> {
    // DuckDB のデータベースファイルを開く（なければ自動作成）
    let conn = Connection::open("database.duckdb").map_err(|e| e.to_string())?;
    
    // サンプルのテーブル作成（最初だけ実行）
    conn.execute("CREATE TABLE IF NOT EXISTS timeseries (timestamp TIMESTAMP, value DOUBLE)", [])
        .map_err(|e| e.to_string())?;

    // 仮のデータを挿入（本番環境ではデータをバルクインサートする）
    conn.execute("INSERT INTO timeseries VALUES (NOW(), 123.45)", [])
        .map_err(|e| e.to_string())?;

    // データを取得
    let mut stmt = conn.prepare("SELECT timestamp, value FROM timeseries ORDER BY timestamp DESC")
        .map_err(|e| e.to_string())?;
    let mut rows = stmt.query([]).map_err(|e| e.to_string())?;

    // 結果を文字列のリストに変換
    let mut result = Vec::new();
    while let Some(row) = rows.next().map_err(|e| e.to_string())? {
        let timestamp: String = row.get(0).map_err(|e| e.to_string())?;
        let value: f64 = row.get(1).map_err(|e| e.to_string())?;
        result.push(format!("{}: {}", timestamp, value));
    }
    
    Ok(result)
}


import { invoke } from "@tauri-apps/api/tauri";
import { useState, useEffect } from "react";

export default function TimeSeries() {
  const [data, setData] = useState([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await invoke("get_time_series_data");
        setData(result);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
    }
    fetchData();
  }, []);

  return (
    <div>
      <h1>Time Series Data</h1>
      <ul>
        {data.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
