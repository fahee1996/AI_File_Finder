"""
AI File Finder - HTTP Server
Production-ready backend server
"""
import sys
from pathlib import Path

# Add backend directory to path
if getattr(sys, 'frozen', False):
    # Running as exe
    backend_dir = Path(sys._MEIPASS)
else:
    backend_dir = Path(__file__).parent

sys.path.insert(0, str(backend_dir))

"""
Simple HTTP server for frontend communication
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from api.server import FileFinderAPI
from utils.logger import setup_logger
import json
from pathlib import Path

logger = setup_logger('http_server')

app = Flask(__name__)
CORS(app)  # Allow frontend to access

# Initialize API
api = FileFinderAPI()



@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        result = api.chat(message)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/search', methods=['POST'])
def search():
    """Handle search requests"""
    try:
        data = request.json
        result = api.search(
            query=data.get('query', ''),
            max_results=data.get('max_results', 10),
            file_type=data.get('file_type')
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get indexing statistics"""
    try:
        result = api.get_indexing_stats()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/index', methods=['POST'])
def index_directory():
    """Index a directory with real-time progress"""
    try:
        data = request.json
        path = data.get('path', '')
        recursive = data.get('recursive', True)
        force = data.get('force', False)
        
        if not path:
            return jsonify({'success': False, 'error': 'Path is required'})
        
        # Validate path exists
        from pathlib import Path
        path_obj = Path(path)
        if not path_obj.exists():
            return jsonify({'success': False, 'error': f'Path does not exist: {path}'})
        
        if not path_obj.is_dir():
            return jsonify({'success': False, 'error': f'Path is not a directory: {path}'})
        
        logger.info(f"Starting indexing: {path}")
        
        # Start indexing
        result = api.start_indexing(path=path, recursive=recursive, force=force)
        
        if result['success']:
            logger.info(f"Indexing completed: {result['result']}")
            return jsonify(result)
        else:
            logger.error(f"Indexing failed: {result.get('error')}")
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Indexing error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file/open', methods=['POST'])
def open_file():
    """Open a file"""
    try:
        data = request.json
        result = api.open_file(data.get('path', ''))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Open file error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file/show', methods=['POST'])
def show_in_folder():
    """Show file in folder"""
    try:
        data = request.json
        result = api.show_in_folder(data.get('path', ''))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Show folder error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file/copy-path', methods=['POST'])
def copy_path():
    """Copy file path to clipboard"""
    try:
        data = request.json
        result = api.copy_path(data.get('path', ''))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Copy path error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file/move', methods=['POST'])
def move_file():
    """Move a file"""
    try:
        data = request.json
        result = api.move_file(
            source=data.get('source', ''),
            destination=data.get('destination', ''),
            overwrite=data.get('overwrite', False)
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Move file error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file/rename', methods=['POST'])
def rename_file():
    """Rename a file"""
    try:
        data = request.json
        result = api.rename_file(
            file_path=data.get('path', ''),
            new_name=data.get('new_name', '')
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Rename file error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/file/delete', methods=['POST'])
def delete_file():
    """Delete a file"""
    try:
        data = request.json
        result = api.delete_file(
            file_path=data.get('path', ''),
            permanent=data.get('permanent', False)
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Delete file error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

import json
from pathlib import Path

# Settings file path
SETTINGS_FILE = Path(__file__).parent / 'data' / 'settings.json'

try:
    from config_prod import SETTINGS_FILE, DATA_DIR
    SETTINGS_FILE = Path(SETTINGS_FILE)
    print(f"[Production] Using settings: {SETTINGS_FILE}")
except ImportError:
    # Development mode
    SETTINGS_FILE = Path(__file__).parent / 'data' / 'settings.json'
    print(f"[Development] Using settings: {SETTINGS_FILE}")

def get_default_settings():
    """Get default settings"""
    return {
        'index_paths': [],
        'excluded_extensions': [
            '.exe', '.dll', '.so', '.dylib',
            '.sys', '.tmp', '.log', '.cache',
            '.bin', '.dat', '.iso'
        ],
        'excluded_folders': [
            'node_modules', '__pycache__', '.git',
            'venv', 'env', '.venv', 'target',
            '.idea', '.vscode', 'dist', 'build'
        ],
        'max_file_size': 50,
        'auto_index': False,
        'llm_model': 'llama3.2:3b'
    }

def load_settings():
    """Load settings from file"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                saved_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                default_settings = get_default_settings()
                default_settings.update(saved_settings)
                return default_settings
        except Exception as e:
            logger.error(f"Error loading settings file: {e}")
            return get_default_settings()
    return get_default_settings()

def save_settings_file(settings_data):
    """Save settings to file"""
    try:
        SETTINGS_FILE.parent.mkdir(exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings_data, f, indent=2)
        logger.info("Settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return False

def apply_settings_to_config(settings_data):
    """Apply settings to runtime config"""
    try:
        from config import config
        
        if 'excluded_extensions' in settings_data:
            config.EXCLUDED_EXTENSIONS = settings_data['excluded_extensions']
            logger.info(f"Updated excluded extensions: {len(config.EXCLUDED_EXTENSIONS)} items")
        
        if 'excluded_folders' in settings_data:
            config.EXCLUDED_FOLDERS = settings_data['excluded_folders']
            logger.info(f"Updated excluded folders: {len(config.EXCLUDED_FOLDERS)} items")
        
        if 'max_file_size' in settings_data:
            config.MAX_FILE_SIZE_MB = int(settings_data['max_file_size'])
            logger.info(f"Updated max file size: {config.MAX_FILE_SIZE_MB} MB")
        
        if 'llm_model' in settings_data:
            config.LLM_MODEL = settings_data['llm_model']
            logger.info(f"Updated LLM model: {config.LLM_MODEL}")
        
        return True
    except Exception as e:
        logger.error(f"Error applying settings to config: {e}")
        return False

# Load and apply saved settings on startup
logger.info("Loading saved settings...")
saved_settings = load_settings()
apply_settings_to_config(saved_settings)
logger.info("Settings loaded and applied")


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    try:
        settings_data = load_settings()
        return jsonify({'success': True, 'settings': settings_data})
    except Exception as e:
        logger.error(f"Error loading settings: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        data = request.json
        
        # Save to file
        if save_settings_file(data):
            # Apply to runtime config
            apply_settings_to_config(data)
            
            return jsonify({
                'success': True,
                'message': 'Settings saved and applied successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save settings'
            })
    except Exception as e:
        logger.error(f"Error saving settings: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings/reset', methods=['POST'])
def reset_settings():
    """Reset settings to defaults"""
    try:
        default_settings = get_default_settings()
        save_settings_file(default_settings)
        apply_settings_to_config(default_settings)
        
        return jsonify({
            'success': True,
            'message': 'Settings reset to defaults',
            'settings': default_settings
        })
    except Exception as e:
        logger.error(f"Error resetting settings: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})



if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 AI File Finder Backend Server")
    print("="*70)
    print("Server running at: http://localhost:5000")
    print("API endpoints available at: http://localhost:5000/api/*")
    print("Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    logger.info("Starting HTTP server on http://localhost:5000")
    
    # Run server
    app.run(
        host='localhost',
        port=5000,
        debug=False,
        threaded=True
    )