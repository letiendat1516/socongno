"""
Entry point của ứng dụng Quản lý Sổ Công Nợ.

Module này khởi tạo ứng dụng, database, migrations và hiển thị main window.
"""
import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from core.paths import get_log_path
from core.database import get_db
from core.migrations import run_migrations
from core.backup_service import BackupService
from views.main_window import MainWindow


def setup_logging() -> None:
    """
    Thiết lập logging cho ứng dụng.
    
    Ghi log vào file và console.
    """
    log_path = get_log_path()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Khởi động ứng dụng Quản lý Sổ Công Nổ")
    logger.info(f"Log file: {log_path}")
    logger.info("=" * 50)


def init_database() -> None:
    """
    Khởi tạo database và chạy migrations.
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Khởi tạo database connection
        db = get_db()
        logger.info("Database connection initialized")
        
        # Chạy migrations
        run_migrations()
        logger.info("Migrations completed")
        
    except Exception as e:
        logger.error(f"Lỗi khi khởi tạo database: {e}", exc_info=True)
        raise


def run_auto_backup() -> None:
    """
    Chạy auto backup nếu cần.
    """
    logger = logging.getLogger(__name__)
    
    try:
        backup_service = BackupService()
        backup_path = backup_service.auto_backup_if_needed()
        
        if backup_path:
            logger.info(f"Auto backup đã tạo: {backup_path}")
        else:
            logger.info("Không cần auto backup")
            
    except Exception as e:
        logger.error(f"Lỗi khi auto backup: {e}", exc_info=True)
        # Không raise exception, cho phép app chạy tiếp


def main() -> int:
    """
    Hàm main của ứng dụng.
    
    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    try:
        # Setup logging
        setup_logging()
        
        # Initialize database
        init_database()
        
        # Run auto backup
        run_auto_backup()
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Sổ Công Nợ")
        app.setOrganizationName("SoCongNo")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Run event loop
        return app.exec()
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.critical(f"Lỗi nghiêm trọng: {e}", exc_info=True)
        
        # Hiển thị error dialog nếu có thể
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            QMessageBox.critical(
                None,
                "Lỗi",
                f"Ứng dụng gặp lỗi nghiêm trọng:\n\n{str(e)}\n\nVui lòng kiểm tra log file."
            )
        except:
            pass
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
