"""
Màn hình quản lý khách hàng.

Module này cung cấp giao diện quản lý khách hàng với PySide6.
"""
import logging
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QTextEdit,
    QDialogButtonBox, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from controllers.customer_controller import CustomerController
from models.customer import Customer
from models.transaction import TransactionType


logger = logging.getLogger(__name__)


class CustomerScreen(QWidget):
    """
    Widget hiển thị màn hình quản lý khách hàng.
    
    Bao gồm table hiển thị danh sách và các nút thao tác.
    """
    
    def __init__(self) -> None:
        """Khởi tạo customer screen."""
        super().__init__()
        self.controller = CustomerController()
        self._init_ui()
        self.refresh_table()
    
    def _init_ui(self) -> None:
        """Khởi tạo giao diện."""
        layout = QVBoxLayout()
        
        # Table hiển thị danh sách khách hàng
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "STT", "Tên", "Số điện thoại", "Địa chỉ", "Tổng nợ (VNĐ)"
        ])
        
        # Thiết lập table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Thêm khách hàng")
        self.btn_add.clicked.connect(self._on_add_customer)
        button_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("Sửa")
        self.btn_edit.clicked.connect(self._on_edit_customer)
        button_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("Xóa")
        self.btn_delete.clicked.connect(self._on_delete_customer)
        button_layout.addWidget(self.btn_delete)
        
        button_layout.addStretch()
        
        self.btn_loan = QPushButton("Cho vay")
        self.btn_loan.clicked.connect(self._on_add_loan)
        button_layout.addWidget(self.btn_loan)
        
        self.btn_payment = QPushButton("Thu nợ")
        self.btn_payment.clicked.connect(self._on_add_payment)
        button_layout.addWidget(self.btn_payment)
        
        self.btn_history = QPushButton("Xem lịch sử")
        self.btn_history.clicked.connect(self._on_view_history)
        button_layout.addWidget(self.btn_history)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def refresh_table(self) -> None:
        """Làm mới bảng danh sách khách hàng."""
        success, message, customers = self.controller.get_all_customers()
        
        if not success:
            QMessageBox.critical(self, "Lỗi", message)
            return
        
        self.table.setRowCount(0)
        
        for idx, customer in enumerate(customers):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # STT
            self.table.setItem(row, 0, QTableWidgetItem(str(idx + 1)))
            
            # Tên
            self.table.setItem(row, 1, QTableWidgetItem(customer.name))
            
            # Số điện thoại
            self.table.setItem(row, 2, QTableWidgetItem(customer.phone))
            
            # Địa chỉ
            self.table.setItem(row, 3, QTableWidgetItem(customer.address))
            
            # Tổng nợ
            success_debt, _, debt = self.controller.get_customer_debt(customer.id)
            debt_text = self._format_money(debt) if success_debt else "N/A"
            item = QTableWidgetItem(debt_text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, item)
            
            # Lưu customer ID vào row
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, customer.id)
    
    def _format_money(self, amount: float) -> str:
        """
        Format số tiền theo định dạng 1,000,000 VNĐ.
        
        Args:
            amount: Số tiền
            
        Returns:
            str: Chuỗi đã format
        """
        return f"{amount:,.0f}"
    
    def _get_selected_customer_id(self) -> Optional[int]:
        """
        Lấy ID của customer đang được chọn.
        
        Returns:
            Optional[int]: Customer ID hoặc None nếu không có selection
        """
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        customer_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        return customer_id
    
    def _on_add_customer(self) -> None:
        """Xử lý sự kiện thêm khách hàng."""
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, phone, address = dialog.get_data()
            success, message, _ = self.controller.create_customer(name, phone, address)
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def _on_edit_customer(self) -> None:
        """Xử lý sự kiện sửa khách hàng."""
        customer_id = self._get_selected_customer_id()
        if not customer_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng cần sửa")
            return
        
        # Lấy thông tin hiện tại
        row = self.table.currentRow()
        name = self.table.item(row, 1).text()
        phone = self.table.item(row, 2).text()
        address = self.table.item(row, 3).text()
        
        dialog = CustomerDialog(self, name, phone, address)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, phone, address = dialog.get_data()
            customer = Customer(id=customer_id, name=name, phone=phone, address=address)
            success, message, _ = self.controller.update_customer(customer)
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def _on_delete_customer(self) -> None:
        """Xử lý sự kiện xóa khách hàng."""
        customer_id = self._get_selected_customer_id()
        if not customer_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng cần xóa")
            return
        
        # Confirm dialog
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa khách hàng này?\nTất cả giao dịch liên quan cũng sẽ bị xóa.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message, _ = self.controller.delete_customer(customer_id)
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def _on_add_loan(self) -> None:
        """Xử lý sự kiện cho vay."""
        customer_id = self._get_selected_customer_id()
        if not customer_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng")
            return
        
        dialog = TransactionDialog(self, "Cho vay")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount, note = dialog.get_data()
            success, message, _ = self.controller.add_loan(customer_id, amount, note)
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def _on_add_payment(self) -> None:
        """Xử lý sự kiện thu nợ."""
        customer_id = self._get_selected_customer_id()
        if not customer_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng")
            return
        
        dialog = TransactionDialog(self, "Thu nợ")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount, note = dialog.get_data()
            success, message, _ = self.controller.add_payment(customer_id, amount, note)
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def _on_view_history(self) -> None:
        """Xử lý sự kiện xem lịch sử."""
        customer_id = self._get_selected_customer_id()
        if not customer_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng")
            return
        
        row = self.table.currentRow()
        customer_name = self.table.item(row, 1).text()
        
        dialog = HistoryDialog(self, customer_id, customer_name)
        dialog.exec()


class CustomerDialog(QDialog):
    """Dialog để thêm/sửa khách hàng."""
    
    def __init__(self, parent: QWidget, name: str = "", phone: str = "", address: str = "") -> None:
        """
        Khởi tạo customer dialog.
        
        Args:
            parent: Widget cha
            name: Tên khách hàng (cho edit mode)
            phone: Số điện thoại (cho edit mode)
            address: Địa chỉ (cho edit mode)
        """
        super().__init__(parent)
        self.setWindowTitle("Thông tin khách hàng")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.txt_name = QLineEdit(name)
        layout.addRow("Tên khách hàng:", self.txt_name)
        
        self.txt_phone = QLineEdit(phone)
        layout.addRow("Số điện thoại:", self.txt_phone)
        
        self.txt_address = QLineEdit(address)
        layout.addRow("Địa chỉ:", self.txt_address)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_data(self) -> tuple[str, str, str]:
        """
        Lấy dữ liệu từ form.
        
        Returns:
            tuple[str, str, str]: (name, phone, address)
        """
        return (
            self.txt_name.text(),
            self.txt_phone.text(),
            self.txt_address.text()
        )


class TransactionDialog(QDialog):
    """Dialog để thêm giao dịch (cho vay/thu nợ)."""
    
    def __init__(self, parent: QWidget, transaction_type: str) -> None:
        """
        Khởi tạo transaction dialog.
        
        Args:
            parent: Widget cha
            transaction_type: Loại giao dịch ("Cho vay" hoặc "Thu nợ")
        """
        super().__init__(parent)
        self.setWindowTitle(transaction_type)
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.txt_amount = QLineEdit()
        self.txt_amount.setPlaceholderText("Nhập số tiền")
        layout.addRow("Số tiền (VNĐ):", self.txt_amount)
        
        self.txt_note = QTextEdit()
        self.txt_note.setPlaceholderText("Nhập ghi chú (tùy chọn)")
        self.txt_note.setMaximumHeight(100)
        layout.addRow("Ghi chú:", self.txt_note)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def _on_accept(self) -> None:
        """Validate và accept dialog."""
        try:
            amount = float(self.txt_amount.text().replace(",", "").strip())
            if amount <= 0:
                raise ValueError()
            self.accept()
        except (ValueError, AttributeError):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số tiền hợp lệ (lớn hơn 0)")
    
    def get_data(self) -> tuple[float, str]:
        """
        Lấy dữ liệu từ form.
        
        Returns:
            tuple[float, str]: (amount, note)
        """
        amount = float(self.txt_amount.text().replace(",", "").strip())
        note = self.txt_note.toPlainText()
        return amount, note


class HistoryDialog(QDialog):
    """Dialog hiển thị lịch sử giao dịch."""
    
    def __init__(self, parent: QWidget, customer_id: int, customer_name: str) -> None:
        """
        Khởi tạo history dialog.
        
        Args:
            parent: Widget cha
            customer_id: ID của customer
            customer_name: Tên customer
        """
        super().__init__(parent)
        self.customer_id = customer_id
        self.setWindowTitle(f"Lịch sử giao dịch - {customer_name}")
        self.setMinimumSize(800, 500)
        
        layout = QVBoxLayout()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "STT", "Ngày giờ", "Loại", "Số tiền (VNĐ)", "Ghi chú"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Close button
        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)
        
        self._load_history()
    
    def _load_history(self) -> None:
        """Load lịch sử giao dịch."""
        controller = CustomerController()
        
        try:
            from services.debt_service import DebtService
            debt_service = DebtService()
            transactions = debt_service.get_customer_history(self.customer_id)
            
            self.table.setRowCount(0)
            
            for idx, trans in enumerate(transactions):
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # STT
                self.table.setItem(row, 0, QTableWidgetItem(str(idx + 1)))
                
                # Ngày giờ
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(trans.created_at)
                    date_str = dt.strftime("%d/%m/%Y %H:%M:%S")
                except:
                    date_str = trans.created_at
                self.table.setItem(row, 1, QTableWidgetItem(date_str))
                
                # Loại
                type_text = "Cho vay" if trans.transaction_type == TransactionType.CHO_VAY else "Thu nợ"
                self.table.setItem(row, 2, QTableWidgetItem(type_text))
                
                # Số tiền
                amount_text = f"{trans.amount:,.0f}"
                item = QTableWidgetItem(amount_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 3, item)
                
                # Ghi chú
                self.table.setItem(row, 4, QTableWidgetItem(trans.note))
                
        except Exception as e:
            logger.error(f"Lỗi khi load lịch sử: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải lịch sử: {str(e)}")
