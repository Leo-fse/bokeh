#[tauri::command]
fn generate_bokeh_plot() -> Value {
    let exe_dir = env::current_exe()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf();

    let python_home = resource_dir().unwrap().join("bin");
    let python_path = python_home.join("python.exe");
    let script_path = python_home.join("scripts/bokeh_json.py");

    let output: Output = Command::new(&python_path)
        .arg(script_path)
        .env("PYTHONHOME", &python_home)
        .env("PYTHONUNBUFFERED", "1")
        .output()
        .expect("Failed to execute Python script");

    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();

    println!("Python Output (Raw): {}", stdout); // ✅ Rust 側でデバッグ

    let json_output: Value = match serde_json::from_str(&stdout) {
        Ok(parsed) => parsed,
        Err(_) => {
            println!("JSON Parse Error: {}", stdout);
            json!({"error": "Invalid JSON", "raw_output": stdout})
        }
    };

    json!({
        "stdout": json_output,
        "stderr": stderr
    })
}