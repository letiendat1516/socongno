"""
Data model cho Transaction (Giao dịch).

Module này định nghĩa cấu trúc dữ liệu cho giao dịch cho vay/thu nợ.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class TransactionType(Enum):
    """
    Enum cho loại giao dịch.
    
    CHO_VAY: Cho khách hàng vay (tăng nợ)
    THU_NO: Thu nợ từ khách hàng (giảm nợ)
    """
    
    CHO_VAY = "CHO_VAY"
    THU_NO = "THU_NO"


@dataclass
class Transaction:
    """
    Model cho giao dịch.
    
    Attributes:
        customer_id: ID của khách hàng
        amount: Số tiền giao dịch
        transaction_type: Loại giao dịch (CHO_VAY hoặc THU_NO)
        note: Ghi chú
        id: ID tự động tăng (None khi tạo mới)
        created_at: Thời gian tạo
    """
    
    customer_id: int
    amount: float
    transaction_type: TransactionType
    note: str = ""
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Chuyển Transaction object thành dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary chứa thông tin transaction
        """
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type.value,
            'note': self.note,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """
        Tạo Transaction object từ dictionary.
        
        Args:
            data: Dictionary chứa thông tin transaction
            
        Returns:
            Transaction: Transaction object mới
        """
        # Parse transaction_type
        trans_type = data.get('transaction_type', 'CHO_VAY')
        if isinstance(trans_type, str):
            trans_type = TransactionType(trans_type)
        
        return cls(
            id=data.get('id'),
            customer_id=data.get('customer_id', 0),
            amount=data.get('amount', 0.0),
            transaction_type=trans_type,
            note=data.get('note', ''),
            created_at=data.get('created_at', datetime.now().isoformat())
        )
