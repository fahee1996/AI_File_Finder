// // // Prevents additional console window on Windows in release, DO NOT REMOVE!!
// // #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// // fn main() {
// //     frontend_lib::run()
// // }


// // Prevents additional console window on Windows in release
// #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// use std::process::{Command, Stdio};
// use std::io::{BufRead, BufReader, Write};
// use std::sync::Mutex;
// use tauri::State;
// use serde::{Deserialize, Serialize};

// #[derive(Debug, Serialize, Deserialize)]
// struct ApiCommand {
//     action: String,
//     params: serde_json::Value,
// }

// #[derive(Debug, Serialize, Deserialize)]
// struct ApiResponse {
//     success: bool,
//     #[serde(skip_serializing_if = "Option::is_none")]
//     response: Option<String>,
//     #[serde(skip_serializing_if = "Option::is_none")]
//     results: Option<Vec<serde_json::Value>>,
//     #[serde(skip_serializing_if = "Option::is_none")]
//     error: Option<String>,
//     #[serde(skip_serializing_if = "Option::is_none")]
//     stats: Option<serde_json::Value>,
//     #[serde(skip_serializing_if = "Option::is_none")]
//     message: Option<String>,
// }

// struct PythonBridge {
//     process: Mutex<Option<std::process::Child>>,
// }

// impl PythonBridge {
//     fn new() -> Self {
//         PythonBridge {
//             process: Mutex::new(None),
//         }
//     }

//     fn start(&self) -> Result<(), String> {
//         let mut process_guard = self.process.lock().unwrap();
        
//         if process_guard.is_some() {
//             return Ok(());
//         }

//         // Get the path to the Python script
//         // In development, use relative path
//         // In production, bundle with the app
//         let python_script = if cfg!(debug_assertions) {
//             "../backend/tauri_bridge.py"
//         } else {
//             // TODO: Update this path for production
//             "../backend/tauri_bridge.py"
//         };

//         let child = Command::new("python")
//             .arg(python_script)
//             .stdin(Stdio::piped())
//             .stdout(Stdio::piped())
//             .stderr(Stdio::piped())
//             .spawn()
//             .map_err(|e| format!("Failed to start Python bridge: {}", e))?;

//         *process_guard = Some(child);
//         Ok(())
//     }

//     fn send_command(&self, command: ApiCommand) -> Result<ApiResponse, String> {
//         let mut process_guard = self.process.lock().unwrap();
        
//         if let Some(ref mut child) = *process_guard {
//             // Write command to stdin
//             if let Some(ref mut stdin) = child.stdin {
//                 let command_json = serde_json::to_string(&command)
//                     .map_err(|e| format!("JSON serialization error: {}", e))?;
                
//                 writeln!(stdin, "{}", command_json)
//                     .map_err(|e| format!("Failed to write to Python: {}", e))?;
                
//                 stdin.flush()
//                     .map_err(|e| format!("Failed to flush: {}", e))?;
//             } else {
//                 return Err("Python stdin not available".to_string());
//             }

//             // Read response from stdout
//             if let Some(ref mut stdout) = child.stdout {
//                 let mut reader = BufReader::new(stdout);
//                 let mut response_line = String::new();
                
//                 reader.read_line(&mut response_line)
//                     .map_err(|e| format!("Failed to read from Python: {}", e))?;
                
//                 let response: ApiResponse = serde_json::from_str(&response_line)
//                     .map_err(|e| format!("JSON parse error: {}", e))?;
                
//                 return Ok(response);
//             } else {
//                 return Err("Python stdout not available".to_string());
//             }
//         }

//         Err("Python bridge not started".to_string())
//     }
// }

// #[tauri::command]
// async fn chat(message: String, bridge: State<'_, PythonBridge>) -> Result<ApiResponse, String> {
//     bridge.start()?;
    
//     let command = ApiCommand {
//         action: "chat".to_string(),
//         params: serde_json::json!({ "message": message }),
//     };
    
//     bridge.send_command(command)
// }

// #[tauri::command]
// async fn search(
//     query: String,
//     max_results: Option<u32>,
//     file_type: Option<String>,
//     bridge: State<'_, PythonBridge>
// ) -> Result<ApiResponse, String> {
//     bridge.start()?;
    
//     let command = ApiCommand {
//         action: "search".to_string(),
//         params: serde_json::json!({
//             "query": query,
//             "max_results": max_results.unwrap_or(10),
//             "file_type": file_type
//         }),
//     };
    
//     bridge.send_command(command)
// }

// #[tauri::command]
// async fn get_stats(bridge: State<'_, PythonBridge>) -> Result<ApiResponse, String> {
//     bridge.start()?;
    
//     let command = ApiCommand {
//         action: "get_stats".to_string(),
//         params: serde_json::json!({}),
//     };
    
//     bridge.send_command(command)
// }

// #[tauri::command]
// async fn index_directory(
//     path: String,
//     recursive: bool,
//     force: bool,
//     bridge: State<'_, PythonBridge>
// ) -> Result<ApiResponse, String> {
//     bridge.start()?;
    
//     let command = ApiCommand {
//         action: "index_directory".to_string(),
//         params: serde_json::json!({
//             "path": path,
//             "recursive": recursive,
//             "force": force
//         }),
//     };
    
//     bridge.send_command(command)
// }

// #[tauri::command]
// async fn open_file(path: String, bridge: State<'_, PythonBridge>) -> Result<ApiResponse, String> {
//     bridge.start()?;
    
//     let command = ApiCommand {
//         action: "open_file".to_string(),
//         params: serde_json::json!({ "path": path }),
//     };
    
//     bridge.send_command(command)
// }

// #[tauri::command]
// async fn show_in_folder(path: String, bridge: State<'_, PythonBridge>) -> Result<ApiResponse, String> {
//     bridge.start()?;
    
//     let command = ApiCommand {
//         action: "show_in_folder".to_string(),
//         params: serde_json::json!({ "path": path }),
//     };
    
//     bridge.send_command(command)
// }

// #[tauri::command]
// async fn copy_path(path: String, bridge: State<'_, PythonBridge>) -> Result<ApiResponse, String> {
//     bridge.start()?;
    
//     let command = ApiCommand {
//         action: "copy_path".to_string(),
//         params: serde_json::json!({ "path": path }),
//     };
    
//     bridge.send_command(command)
// }

// fn main() {
//     let bridge = PythonBridge::new();
    
//     tauri::Builder::default()
//         .manage(bridge)
//         .invoke_handler(tauri::generate_handler![
//             chat,
//             search,
//             get_stats,
//             index_directory,
//             open_file,
//             show_in_folder,
//             copy_path
//         ])
//         .run(tauri::generate_context!())
//         .expect("error while running tauri application");
// }

// // Prevents additional console window on Windows in release
// #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// fn main() {
//     tauri::Builder::default()
//         .run(tauri::generate_context!())
//         .expect("error while running tauri application");
// }

// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod backend;

fn main() {
    // Start backend server
    if let Err(e) = backend::start_backend() {
        eprintln!("Failed to start backend: {}", e);
    }
    
    // Small delay to let backend start
    std::thread::sleep(std::time::Duration::from_secs(2));
    
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}