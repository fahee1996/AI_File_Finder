use std::process::{Command, Stdio};
use std::env;
use std::path::PathBuf;

pub fn start_backend() -> Result<(), String> {
    // Get the resource path
    let resource_dir = get_resource_dir()?;
    let backend_exe = resource_dir.join("backend-dist").join("backend.exe");
    
    if !backend_exe.exists() {
        return Err(format!("Backend not found at: {:?}", backend_exe));
    }
    
    // Start backend as detached process
    Command::new(backend_exe)
        .current_dir(resource_dir.join("backend-dist"))
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("Failed to start backend: {}", e))?;
    
    Ok(())
}

fn get_resource_dir() -> Result<PathBuf, String> {
    // In development
    if cfg!(debug_assertions) {
        return Ok(PathBuf::from("../"));
    }
    
    // In production
    let exe_path = env::current_exe()
        .map_err(|e| format!("Failed to get exe path: {}", e))?;
    
    let exe_dir = exe_path.parent()
        .ok_or("Failed to get exe directory")?;
    
    Ok(exe_dir.to_path_buf())
}