"""
Controller xử lý events từ UI cho Customer.

Module này nhận events từ UI, gọi service layer và trả về kết quả.
"""
import logging
from typing import Tuple, List, Any, Optional
from models.customer import Customer
from repositories.customer_repo import CustomerRepository
from services.debt_service import DebtService


logger = logging.getLogger(__name__)


class CustomerController:
    """
    Controller xử lý các thao tác liên quan đến customer.
    
    Nhận events từ UI, xử lý errors và trả về kết quả.
    """
    
    def __init__(self) -> None:
        """Khởi tạo customer controller."""
        self.customer_repo = CustomerRepository()
        self.debt_service = DebtService()
    
    def create_customer(self, name: str, phone: str, address: str) -> Tuple[bool, str, Optional[Customer]]:
        """
        Tạo customer mới.
        
        Args:
            name: Tên khách hàng
            phone: Số điện thoại
            address: Địa chỉ
            
        Returns:
            Tuple[bool, str, Optional[Customer]]: (success, message, customer_object)
        """
        try:
            # Validate input
            if not name or not name.strip():
                return False, "Tên khách hàng không được để trống", None
            
            customer = Customer(
                name=name.strip(),
                phone=phone.strip(),
                address=address.strip()
            )
            
            result = self.customer_repo.create(customer)
            logger.info(f"Đã tạo khách hàng: {result.name}")
            
            return True, "Tạo khách hàng thành công", result
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo khách hàng: {e}")
            return False, f"Lỗi: {str(e)}", None
    
    def update_customer(self, customer: Customer) -> Tuple[bool, str, None]:
        """
        Cập nhật thông tin customer.
        
        Args:
            customer: Customer object với thông tin mới
            
        Returns:
            Tuple[bool, str, None]: (success, message, None)
        """
        try:
            # Validate input
            if not customer.name or not customer.name.strip():
                return False, "Tên khách hàng không được để trống", None
            
            if not customer.id:
                return False, "ID khách hàng không hợp lệ", None
            
            success = self.customer_repo.update(customer)
            
            if success:
                logger.info(f"Đã cập nhật khách hàng: {customer.name}")
                return True, "Cập nhật khách hàng thành công", None
            else:
                return False, "Không tìm thấy khách hàng", None
                
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật khách hàng: {e}")
            return False, f"Lỗi: {str(e)}", None
    
    def delete_customer(self, customer_id: int) -> Tuple[bool, str, None]:
        """
        Xóa customer.
        
        Args:
            customer_id: ID của customer cần xóa
            
        Returns:
            Tuple[bool, str, None]: (success, message, None)
        """
        try:
            success = self.customer_repo.delete(customer_id)
            
            if success:
                logger.info(f"Đã xóa khách hàng ID: {customer_id}")
                return True, "Xóa khách hàng thành công", None
            else:
                return False, "Không tìm thấy khách hàng", None
                
        except Exception as e:
            logger.error(f"Lỗi khi xóa khách hàng: {e}")
            return False, f"Lỗi: {str(e)}", None
    
    def get_all_customers(self) -> Tuple[bool, str, List[Customer]]:
        """
        Lấy danh sách tất cả customers.
        
        Returns:
            Tuple[bool, str, List[Customer]]: (success, message, customers_list)
        """
        try:
            customers = self.customer_repo.get_all()
            return True, "", customers
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách khách hàng: {e}")
            return False, f"Lỗi: {str(e)}", []
    
    def add_loan(self, customer_id: int, amount: float, note: str) -> Tuple[bool, str, None]:
        """
        Thêm khoản cho vay.
        
        Args:
            customer_id: ID của customer
            amount: Số tiền cho vay
            note: Ghi chú
            
        Returns:
            Tuple[bool, str, None]: (success, message, None)
        """
        try:
            self.debt_service.add_loan(customer_id, amount, note)
            return True, "Đã thêm khoản cho vay thành công", None
            
        except ValueError as e:
            logger.warning(f"Validation error khi thêm cho vay: {e}")
            return False, str(e), None
            
        except Exception as e:
            logger.error(f"Lỗi khi thêm cho vay: {e}")
            return False, f"Lỗi: {str(e)}", None
    
    def add_payment(self, customer_id: int, amount: float, note: str) -> Tuple[bool, str, None]:
        """
        Thêm khoản thu nợ.
        
        Args:
            customer_id: ID của customer
            amount: Số tiền thu nợ
            note: Ghi chú
            
        Returns:
            Tuple[bool, str, None]: (success, message, None)
        """
        try:
            self.debt_service.add_payment(customer_id, amount, note)
            return True, "Đã thu nợ thành công", None
            
        except ValueError as e:
            logger.warning(f"Validation error khi thu nợ: {e}")
            return False, str(e), None
            
        except Exception as e:
            logger.error(f"Lỗi khi thu nợ: {e}")
            return False, f"Lỗi: {str(e)}", None
    
    def get_customer_debt(self, customer_id: int) -> Tuple[bool, str, float]:
        """
        Lấy tổng nợ của customer.
        
        Args:
            customer_id: ID của customer
            
        Returns:
            Tuple[bool, str, float]: (success, message, debt_amount)
        """
        try:
            debt = self.debt_service.calculate_debt(customer_id)
            return True, "", debt
            
        except ValueError as e:
            logger.warning(f"Validation error khi tính nợ: {e}")
            return False, str(e), 0.0
            
        except Exception as e:
            logger.error(f"Lỗi khi tính nợ: {e}")
            return False, f"Lỗi: {str(e)}", 0.0
