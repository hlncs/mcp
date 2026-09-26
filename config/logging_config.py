import logging
import logging.handlers
import json
from datetime import datetime
from typing import Any, Dict
import sys
import os

# Create logs directory
os.makedirs('logs', exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'trace_id'):
            log_data['trace_id'] = record.trace_id
        if hasattr(record, 'span_id'):
            log_data['span_id'] = record.span_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        
        return json.dumps(log_data)

class ContextFilter(logging.Filter):
    """Add context information to log records"""
    
    def __init__(self):
        super().__init__()
        self.trace_id = None
        self.span_id = None
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = self.trace_id
        record.span_id = self.span_id
        return True

# Global context filter
context_filter = ContextFilter()

def setup_logging(
    log_level: str = 'INFO',
    json_format: bool = True,
    log_file: str = 'logs/app.log'
) -> Dict[str, logging.Logger]:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format for logs
        log_file: Path to log file
    
    Returns:
        Dictionary of loggers for different modules
    """
    
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addFilter(context_filter)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.addFilter(context_filter)
    
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # File handler (JSON format)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(JSONFormatter())
    file_handler.addFilter(context_filter)
    root_logger.addHandler(file_handler)
    
    # Module loggers
    loggers = {
        'app': logging.getLogger('app'),
        'backend': logging.getLogger('backend'),
        'sse': logging.getLogger('sse'),
        'agents': logging.getLogger('agents'),
        'api': logging.getLogger('api'),
        'database': logging.getLogger('database'),
        'mcp': logging.getLogger('mcp'),
    }
    
    for logger_name, logger in loggers.items():
        logger.setLevel(log_level)
        logger.addFilter(context_filter)
    
    return loggers

def get_logger(name: str) -> logging.Logger:
    """Get logger by name"""
    return logging.getLogger(name)

def set_trace_context(trace_id: str, span_id: str = None):
    """Set trace context for current thread"""
    context_filter.trace_id = trace_id
    context_filter.span_id = span_id or trace_id