"""
Service quản lý business logic cho công nợ.

Module này chứa tất cả business logic và validation rules.
"""
import logging
from typing import List
from models.transaction import Transaction, TransactionType
from repositories.customer_repo import CustomerRepository
from repositories.transaction_repo import TransactionRepository


logger = logging.getLogger(__name__)


class DebtService:
    """
    Service quản lý business logic cho công nợ.
    
    Xử lý validation và các quy tắc nghiệp vụ.
    """
    
    def __init__(self) -> None:
        """Khởi tạo debt service."""
        self.customer_repo = CustomerRepository()
        self.transaction_repo = TransactionRepository()
    
    def calculate_debt(self, customer_id: int) -> float:
        """
        Tính tổng nợ hiện tại của customer.
        
        Args:
            customer_id: ID của customer
            
        Returns:
            float: Tổng nợ (dương = còn nợ, âm = thừa tiền, 0 = hòa)
            
        Raises:
            ValueError: Nếu customer không tồn tại
        """
        # Validate customer tồn tại
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Không tìm thấy khách hàng với ID: {customer_id}")
        
        return self.transaction_repo.get_customer_balance(customer_id)
    
    def add_loan(self, customer_id: int, amount: float, note: str = "") -> Transaction:
        """
        Thêm khoản cho vay (CHO_VAY).
        
        Args:
            customer_id: ID của customer
            amount: Số tiền cho vay
            note: Ghi chú
            
        Returns:
            Transaction: Transaction đã được tạo
            
        Raises:
            ValueError: Nếu validation fail
        """
        # Validate customer tồn tại
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Không tìm thấy khách hàng với ID: {customer_id}")
        
        # Validate amount > 0
        if amount <= 0:
            raise ValueError("Số tiền cho vay phải lớn hơn 0")
        
        # Tạo transaction
        transaction = Transaction(
            customer_id=customer_id,
            amount=amount,
            transaction_type=TransactionType.CHO_VAY,
            note=note
        )
        
        result = self.transaction_repo.create(transaction)
        logger.info(f"Đã thêm khoản cho vay {amount} cho khách hàng {customer.name}")
        
        return result
    
    def add_payment(self, customer_id: int, amount: float, note: str = "") -> Transaction:
        """
        Thêm khoản thu nợ (THU_NO).
        
        Args:
            customer_id: ID của customer
            amount: Số tiền thu nợ
            note: Ghi chú
            
        Returns:
            Transaction: Transaction đã được tạo
            
        Raises:
            ValueError: Nếu validation fail
        """
        # Validate customer tồn tại
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Không tìm thấy khách hàng với ID: {customer_id}")
        
        # Validate amount > 0
        if amount <= 0:
            raise ValueError("Số tiền thu nợ phải lớn hơn 0")
        
        # Tạo transaction
        transaction = Transaction(
            customer_id=customer_id,
            amount=amount,
            transaction_type=TransactionType.THU_NO,
            note=note
        )
        
        result = self.transaction_repo.create(transaction)
        logger.info(f"Đã thu nợ {amount} từ khách hàng {customer.name}")
        
        return result
    
    def get_customer_history(self, customer_id: int) -> List[Transaction]:
        """
        Lấy lịch sử giao dịch của customer.
        
        Args:
            customer_id: ID của customer
            
        Returns:
            List[Transaction]: Danh sách giao dịch của customer
            
        Raises:
            ValueError: Nếu customer không tồn tại
        """
        # Validate customer tồn tại
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Không tìm thấy khách hàng với ID: {customer_id}")
        
        return self.transaction_repo.get_by_customer_id(customer_id)
