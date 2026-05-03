"""
Bridge between Tauri frontend and Python backend
This script runs as a subprocess from Tauri
"""
import sys
import json
from api.server import FileFinderAPI
from utils.logger import setup_logger

logger = setup_logger('tauri_bridge')

# Initialize API once
api = FileFinderAPI()

def handle_command(command: dict) -> dict:
    """
    Handle commands from Tauri frontend
    
    Args:
        command: Command dict with 'action' and 'params'
        
    Returns:
        Response dict
    """
    action = command.get('action')
    params = command.get('params', {})
    
    try:
        if action == 'chat':
            return api.chat(params.get('message', ''))
        
        elif action == 'search':
            return api.search(
                query=params.get('query', ''),
                max_results=params.get('max_results', 10),
                file_type=params.get('file_type')
            )
        
        elif action == 'get_stats':
            return api.get_indexing_stats()
        
        elif action == 'index_directory':
            return api.start_indexing(
                path=params.get('path', ''),
                recursive=params.get('recursive', True),
                force=params.get('force', False)
            )
        
        elif action == 'open_file':
            return api.open_file(params.get('path', ''))
        
        elif action == 'show_in_folder':
            return api.show_in_folder(params.get('path', ''))
        
        elif action == 'copy_path':
            return api.copy_path(params.get('path', ''))
        
        elif action == 'move_file':
            return api.move_file(
                source=params.get('source', ''),
                destination=params.get('destination', ''),
                overwrite=params.get('overwrite', False)
            )
        
        elif action == 'rename_file':
            return api.rename_file(
                file_path=params.get('path', ''),
                new_name=params.get('new_name', '')
            )
        
        elif action == 'delete_file':
            return api.delete_file(
                file_path=params.get('path', ''),
                permanent=params.get('permanent', False)
            )
        
        elif action == 'clear_context':
            return api.clear_context()
        
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}'
            }
    
    except Exception as e:
        logger.error(f"Error handling command: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Main loop - reads commands from stdin, writes responses to stdout"""
    logger.info("Tauri bridge started")
    
    while True:
        try:
            # Read command from stdin
            line = sys.stdin.readline()
            
            if not line:
                break
            
            # Parse command
            command = json.loads(line.strip())
            
            # Handle command
            response = handle_command(command)
            
            # Write response to stdout
            sys.stdout.write(json.dumps(response) + '\n')
            sys.stdout.flush()
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            error_response = {
                'success': False,
                'error': 'Invalid JSON'
            }
            sys.stdout.write(json.dumps(error_response) + '\n')
            sys.stdout.flush()
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            error_response = {
                'success': False,
                'error': str(e)
            }
            sys.stdout.write(json.dumps(error_response) + '\n')
            sys.stdout.flush()

if __name__ == "__main__":
    main()