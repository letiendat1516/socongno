"""
Repository cho Transaction.

Module này xử lý tất cả các thao tác CRUD với bảng transactions trong database.
"""
import logging
from typing import List, Optional
from core.database import get_db
from models.transaction import Transaction, TransactionType


logger = logging.getLogger(__name__)


class TransactionRepository:
    """
    Repository quản lý CRUD operations cho Transaction.
    
    Chỉ chứa SQL queries, không có business logic.
    """
    
    def __init__(self) -> None:
        """Khởi tạo transaction repository."""
        self.db = get_db()
        self.conn = self.db.get_connection()
    
    def create(self, transaction: Transaction) -> Transaction:
        """
        Tạo transaction mới trong database.
        
        Args:
            transaction: Transaction object cần tạo
            
        Returns:
            Transaction: Transaction object với ID đã được gán
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (customer_id, amount, transaction_type, note, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                transaction.customer_id,
                transaction.amount,
                transaction.transaction_type.value,
                transaction.note,
                transaction.created_at
            )
        )
        self.conn.commit()
        
        transaction.id = cursor.lastrowid
        logger.info(f"Đã tạo transaction mới với ID: {transaction.id}")
        
        return transaction
    
    def get_by_customer_id(self, customer_id: int) -> List[Transaction]:
        """
        Lấy tất cả transactions của một customer.
        
        Args:
            customer_id: ID của customer
            
        Returns:
            List[Transaction]: Danh sách transactions của customer
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM transactions 
            WHERE customer_id = ? 
            ORDER BY created_at DESC
            """,
            (customer_id,)
        )
        rows = cursor.fetchall()
        
        transactions = []
        for row in rows:
            transactions.append(Transaction(
                id=row['id'],
                customer_id=row['customer_id'],
                amount=row['amount'],
                transaction_type=TransactionType(row['transaction_type']),
                note=row['note'] or '',
                created_at=row['created_at']
            ))
        
        return transactions
    
    def get_all(self) -> List[Transaction]:
        """
        Lấy tất cả transactions.
        
        Returns:
            List[Transaction]: Danh sách tất cả transactions
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        transactions = []
        for row in rows:
            transactions.append(Transaction(
                id=row['id'],
                customer_id=row['customer_id'],
                amount=row['amount'],
                transaction_type=TransactionType(row['transaction_type']),
                note=row['note'] or '',
                created_at=row['created_at']
            ))
        
        return transactions
    
    def delete(self, transaction_id: int) -> bool:
        """
        Xóa transaction theo ID.
        
        Args:
            transaction_id: ID của transaction cần xóa
            
        Returns:
            bool: True nếu xóa thành công, False nếu không tìm thấy
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Đã xóa transaction ID: {transaction_id}")
            return True
        else:
            logger.warning(f"Không tìm thấy transaction ID: {transaction_id}")
            return False
    
    def get_customer_balance(self, customer_id: int) -> float:
        """
        Tính tổng nợ của customer (CHO_VAY - THU_NO).
        
        Args:
            customer_id: ID của customer
            
        Returns:
            float: Tổng nợ hiện tại (dương = còn nợ, âm = thừa tiền, 0 = hòa)
        """
        cursor = self.conn.cursor()
        
        # Tính tổng CHO_VAY
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM transactions
            WHERE customer_id = ? AND transaction_type = ?
            """,
            (customer_id, TransactionType.CHO_VAY.value)
        )
        cho_vay = cursor.fetchone()['total']
        
        # Tính tổng THU_NO
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM transactions
            WHERE customer_id = ? AND transaction_type = ?
            """,
            (customer_id, TransactionType.THU_NO.value)
        )
        thu_no = cursor.fetchone()['total']
        
        balance = cho_vay - thu_no
        logger.debug(f"Customer {customer_id}: Cho vay={cho_vay}, Thu nợ={thu_no}, Tổng nợ={balance}")
        
        return balance
