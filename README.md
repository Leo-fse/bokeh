use std::process::Command;
use tauri::AppBuilder;

#[tauri::command]
fn run_python_script(script: String) -> String {
    let python_path = "src-tauri/python_embedded/python.exe";

    let output = Command::new(python_path)
        .arg(script)
        .output()
        .expect("Failed to execute Python script");

    String::from_utf8_lossy(&output.stdout).to_string()
}

pub fn run() {
    AppBuilder::new()
        .invoke_handler(tauri::generate_handler![run_python_script])
        .run(tauri::generate_context!())
        .expect("Tauri application failed to start");
}




