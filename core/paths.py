"""
Quản lý đường dẫn lưu trữ dữ liệu ứng dụng.

Module này cung cấp các hàm để tạo và lấy đường dẫn lưu trữ
dữ liệu ứng dụng trên các nền tảng khác nhau (Windows/Mac/Linux).
"""
import os
from pathlib import Path
from typing import Optional


def get_app_data_dir() -> Path:
    """
    Lấy đường dẫn thư mục dữ liệu ứng dụng.
    
    Tự động phát hiện hệ điều hành và trả về đường dẫn phù hợp:
    - Windows: %APPDATA%/SoCongNo
    - macOS: ~/Library/Application Support/SoCongNo
    - Linux: ~/.local/share/SoCongNo
    
    Returns:
        Path: Đường dẫn đến thư mục dữ liệu ứng dụng
    """
    if os.name == 'nt':  # Windows
        app_data = os.getenv('APPDATA')
        if app_data:
            base_dir = Path(app_data)
        else:
            base_dir = Path.home() / 'AppData' / 'Roaming'
    elif os.name == 'posix':
        import platform
        if platform.system() == 'Darwin':  # macOS
            base_dir = Path.home() / 'Library' / 'Application Support'
        else:  # Linux
            base_dir = Path.home() / '.local' / 'share'
    else:
        # Fallback cho các hệ điều hành khác
        base_dir = Path.home() / '.socongno'
    
    app_dir = base_dir / 'SoCongNo'
    
    # Tự động tạo thư mục nếu chưa tồn tại
    app_dir.mkdir(parents=True, exist_ok=True)
    
    return app_dir


def get_database_path() -> Path:
    """
    Lấy đường dẫn đến file database.
    
    Returns:
        Path: Đường dẫn đầy đủ đến file socongno.db
    """
    return get_app_data_dir() / 'socongno.db'


def get_backup_dir() -> Path:
    """
    Lấy đường dẫn thư mục backup.
    
    Returns:
        Path: Đường dẫn đến thư mục backups
    """
    backup_dir = get_app_data_dir() / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_log_path() -> Path:
    """
    Lấy đường dẫn đến file log.
    
    Returns:
        Path: Đường dẫn đầy đủ đến file socongno.log
    """
    return get_app_data_dir() / 'socongno.log'
