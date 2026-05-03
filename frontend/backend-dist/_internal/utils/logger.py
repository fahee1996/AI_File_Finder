"""Logging configuration for the application"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    use_colors: bool = True
) -> logging.Logger:
    """
    Set up logger with console and optional file handlers
    
    Args:
        name: Logger name
        log_file: Optional log file name (without path)
        level: Logging level
        use_colors: Use colored output in console
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Format strings
    detailed_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    simple_format = '%(levelname)s - %(message)s'
    
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if use_colors:
        console_formatter = ColoredFormatter(simple_format, datefmt=date_format)
    else:
        console_formatter = logging.Formatter(simple_format, datefmt=date_format)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create log file with date
        log_path = log_dir / f"{log_file}_{datetime.now():%Y%m%d}.log"
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level)
        
        file_formatter = logging.Formatter(detailed_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_path}")
    
    return logger

# Create default application logger
logger = setup_logger('ai_file_finder', 'app', level=logging.INFO)

if __name__ == "__main__":
    # Test logging
    test_logger = setup_logger('test', 'test')
    
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")