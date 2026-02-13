"""
Quản lý kết nối và schema của SQLite database.

Module này cung cấp singleton database connection và
khởi tạo schema cho bảng customers và transactions.
"""
import sqlite3
import logging
from pathlib import Path
from typing import Optional
from core.paths import get_database_path


logger = logging.getLogger(__name__)


class Database:
    """
    Singleton class quản lý kết nối SQLite database.
    
    Attributes:
        _instance: Instance duy nhất của Database
        _connection: SQLite connection object
    """
    
    _instance: Optional['Database'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __new__(cls) -> 'Database':
        """Tạo hoặc trả về instance duy nhất của Database."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Khởi tạo database connection nếu chưa có."""
        if self._connection is None:
            self._connect()
    
    def _connect(self) -> None:
        """Tạo kết nối đến SQLite database."""
        db_path = get_database_path()
        logger.info(f"Kết nối đến database: {db_path}")
        
        self._connection = sqlite3.connect(
            str(db_path),
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        
        # Enable foreign keys
        self._connection.execute("PRAGMA foreign_keys = ON")
        
        # Set row factory để trả về dict thay vì tuple
        self._connection.row_factory = sqlite3.Row
        
        logger.info("Kết nối database thành công")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Lấy connection object.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        if self._connection is None:
            self._connect()
        return self._connection
    
    def init_schema(self) -> None:
        """
        Khởi tạo schema cho database.
        
        Tạo 2 bảng chính:
        - customers: Thông tin khách hàng
        - transactions: Giao dịch cho vay/thu nợ
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tạo bảng customers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tạo bảng transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        """)
        
        # Tạo index cho customer_id để tăng tốc query
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_customer_id 
            ON transactions(customer_id)
        """)
        
        conn.commit()
        logger.info("Khởi tạo schema database thành công")
    
    def close(self) -> None:
        """Đóng kết nối database."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Đã đóng kết nối database")


def get_db() -> Database:
    """
    Hàm tiện ích để lấy Database instance.
    
    Returns:
        Database: Database singleton instance
    """
    return Database()
