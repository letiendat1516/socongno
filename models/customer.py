"""
Data model cho Customer (Khách hàng).

Module này định nghĩa cấu trúc dữ liệu cho khách hàng.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Customer:
    """
    Model cho khách hàng.
    
    Attributes:
        id: ID tự động tăng (None khi tạo mới)
        name: Tên khách hàng
        phone: Số điện thoại
        address: Địa chỉ
        created_at: Thời gian tạo
    """
    
    name: str
    phone: str = ""
    address: str = ""
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Chuyển Customer object thành dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary chứa thông tin customer
        """
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Customer':
        """
        Tạo Customer object từ dictionary.
        
        Args:
            data: Dictionary chứa thông tin customer
            
        Returns:
            Customer: Customer object mới
        """
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            created_at=data.get('created_at', datetime.now().isoformat())
        )
