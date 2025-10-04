import os
from pathlib import Path

def setup_environment():
    """Setup environment variables and create necessary directories"""
    # Create base directories if they don't exist
    base_dirs = [
        "logs",
        "data",
        "config",
        "backups",
        "exports"
    ]
    
    for dir_name in base_dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Set environment variables
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("LANGUAGE", "tr")  # Default language
    
    # Load environment variables from .env file if exists
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ.setdefault(key, value)