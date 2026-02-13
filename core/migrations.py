"""
Quản lý migrations và versioning của database schema.

Module này theo dõi version của database schema và
tự động áp dụng các migrations khi cần thiết.
"""
import sqlite3
import logging
from typing import List, Callable
from core.database import get_db


logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Quản lý migrations cho database.
    
    Theo dõi schema version và áp dụng migrations tự động.
    """
    
    def __init__(self) -> None:
        """Khởi tạo migration manager."""
        self.db = get_db()
        self.conn = self.db.get_connection()
        self._ensure_version_table()
    
    def _ensure_version_table(self) -> None:
        """Tạo bảng schema_version nếu chưa tồn tại."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        self.conn.commit()
        logger.info("Đã đảm bảo bảng schema_version tồn tại")
    
    def get_current_version(self) -> int:
        """
        Lấy version hiện tại của database schema.
        
        Returns:
            int: Version hiện tại (0 nếu chưa có migration nào)
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(version) as version FROM schema_version")
        result = cursor.fetchone()
        
        if result and result['version'] is not None:
            return result['version']
        return 0
    
    def _record_migration(self, version: int, description: str) -> None:
        """
        Ghi nhận migration đã được áp dụng.
        
        Args:
            version: Số version của migration
            description: Mô tả migration
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO schema_version (version, description) VALUES (?, ?)",
            (version, description)
        )
        self.conn.commit()
        logger.info(f"Đã ghi nhận migration version {version}: {description}")
    
    def _migration_1_initial_schema(self) -> None:
        """Migration 1: Tạo schema ban đầu."""
        logger.info("Áp dụng migration 1: Tạo schema ban đầu")
        self.db.init_schema()
        self._record_migration(1, "Initial schema - customers and transactions tables")
    
    def apply_migrations(self) -> None:
        """
        Áp dụng tất cả migrations chưa được thực hiện.
        
        Tự động phát hiện version hiện tại và áp dụng các migrations
        tiếp theo theo thứ tự.
        """
        current_version = self.get_current_version()
        logger.info(f"Database hiện tại ở version: {current_version}")
        
        # Danh sách migrations theo thứ tự
        migrations: List[tuple[int, Callable[[], None]]] = [
            (1, self._migration_1_initial_schema),
            # Thêm migrations mới vào đây
        ]
        
        # Áp dụng các migrations chưa thực hiện
        for version, migration_func in migrations:
            if version > current_version:
                logger.info(f"Đang áp dụng migration version {version}")
                try:
                    migration_func()
                    logger.info(f"Migration version {version} thành công")
                except Exception as e:
                    logger.error(f"Lỗi khi áp dụng migration version {version}: {e}")
                    raise
        
        final_version = self.get_current_version()
        if final_version > current_version:
            logger.info(f"Migrations hoàn tất. Database đã được nâng cấp lên version {final_version}")
        else:
            logger.info("Không có migration nào cần áp dụng")


def run_migrations() -> None:
    """
    Hàm tiện ích để chạy migrations.
    
    Được gọi khi khởi động ứng dụng.
    """
    manager = MigrationManager()
    manager.apply_migrations()
