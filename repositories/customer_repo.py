"""
Repository cho Customer.

Module này xử lý tất cả các thao tác CRUD với bảng customers trong database.
"""
import logging
from typing import List, Optional
from core.database import get_db
from models.customer import Customer


logger = logging.getLogger(__name__)


class CustomerRepository:
    """
    Repository quản lý CRUD operations cho Customer.
    
    Chỉ chứa SQL queries, không có business logic.
    """
    
    def __init__(self) -> None:
        """Khởi tạo customer repository."""
        self.db = get_db()
        self.conn = self.db.get_connection()
    
    def create(self, customer: Customer) -> Customer:
        """
        Tạo customer mới trong database.
        
        Args:
            customer: Customer object cần tạo
            
        Returns:
            Customer: Customer object với ID đã được gán
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO customers (name, phone, address, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (customer.name, customer.phone, customer.address, customer.created_at)
        )
        self.conn.commit()
        
        customer.id = cursor.lastrowid
        logger.info(f"Đã tạo customer mới với ID: {customer.id}")
        
        return customer
    
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """
        Lấy customer theo ID.
        
        Args:
            customer_id: ID của customer cần lấy
            
        Returns:
            Optional[Customer]: Customer object nếu tìm thấy, None nếu không
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM customers WHERE id = ?",
            (customer_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return Customer(
                id=row['id'],
                name=row['name'],
                phone=row['phone'] or '',
                address=row['address'] or '',
                created_at=row['created_at']
            )
        return None
    
    def get_all(self) -> List[Customer]:
        """
        Lấy tất cả customers.
        
        Returns:
            List[Customer]: Danh sách tất cả customers
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM customers ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        customers = []
        for row in rows:
            customers.append(Customer(
                id=row['id'],
                name=row['name'],
                phone=row['phone'] or '',
                address=row['address'] or '',
                created_at=row['created_at']
            ))
        
        return customers
    
    def update(self, customer: Customer) -> bool:
        """
        Cập nhật thông tin customer.
        
        Args:
            customer: Customer object với thông tin mới
            
        Returns:
            bool: True nếu update thành công, False nếu không tìm thấy customer
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE customers 
            SET name = ?, phone = ?, address = ?
            WHERE id = ?
            """,
            (customer.name, customer.phone, customer.address, customer.id)
        )
        self.conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Đã cập nhật customer ID: {customer.id}")
            return True
        else:
            logger.warning(f"Không tìm thấy customer ID: {customer.id}")
            return False
    
    def delete(self, customer_id: int) -> bool:
        """
        Xóa customer theo ID.
        
        Args:
            customer_id: ID của customer cần xóa
            
        Returns:
            bool: True nếu xóa thành công, False nếu không tìm thấy customer
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        self.conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Đã xóa customer ID: {customer_id}")
            return True
        else:
            logger.warning(f"Không tìm thấy customer ID: {customer_id}")
            return False
