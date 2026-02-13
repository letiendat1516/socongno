"""
Main window của ứng dụng.

Module này cung cấp cửa sổ chính với menu và tabs.
"""
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QFileDialog,
    QLabel
)
from PySide6.QtCore import Qt
from views.customer_screen import CustomerScreen
from core.backup_service import BackupService
from controllers.customer_controller import CustomerController


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng.
    
    Chứa menu bar, tab widget và status bar.
    """
    
    def __init__(self) -> None:
        """Khởi tạo main window."""
        super().__init__()
        self.backup_service = BackupService()
        self.controller = CustomerController()
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Khởi tạo giao diện."""
        # Thiết lập window
        self.setWindowTitle("Quản lý Sổ Công Nợ")
        self.resize(1000, 600)
        
        # Menu bar
        self._create_menu_bar()
        
        # Tab widget
        self.tabs = QTabWidget()
        self.customer_screen = CustomerScreen()
        self.tabs.addTab(self.customer_screen, "Khách hàng")
        
        self.setCentralWidget(self.tabs)
        
        # Status bar
        self.status_label = QLabel()
        self.statusBar().addPermanentWidget(self.status_label)
        self.update_status_bar()
    
    def _create_menu_bar(self) -> None:
        """Tạo menu bar."""
        menu_bar = self.menuBar()
        
        # Menu File
        file_menu = menu_bar.addMenu("&File")
        
        backup_action = file_menu.addAction("&Backup ngay")
        backup_action.triggered.connect(self._on_backup)
        
        restore_action = file_menu.addAction("&Khôi phục từ backup")
        restore_action.triggered.connect(self._on_restore)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("T&hoát")
        exit_action.triggered.connect(self.close)
        
        # Menu Trợ giúp
        help_menu = menu_bar.addMenu("&Trợ giúp")
        
        about_action = help_menu.addAction("&Giới thiệu")
        about_action.triggered.connect(self._on_about)
    
    def update_status_bar(self) -> None:
        """Cập nhật status bar với tổng số khách hàng và tổng nợ."""
        try:
            success, _, customers = self.controller.get_all_customers()
            
            if not success:
                self.status_label.setText("Lỗi khi tải dữ liệu")
                return
            
            total_customers = len(customers)
            total_debt = 0.0
            
            for customer in customers:
                success_debt, _, debt = self.controller.get_customer_debt(customer.id)
                if success_debt:
                    total_debt += debt
            
            status_text = f"Tổng số khách hàng: {total_customers} | Tổng nợ: {total_debt:,.0f} VNĐ"
            self.status_label.setText(status_text)
            
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật status bar: {e}")
            self.status_label.setText("Lỗi")
    
    def _on_backup(self) -> None:
        """Xử lý sự kiện backup."""
        backup_path = self.backup_service.backup_now()
        
        if backup_path:
            QMessageBox.information(
                self,
                "Thành công",
                f"Backup thành công!\n\nFile backup: {backup_path.name}"
            )
        else:
            QMessageBox.warning(
                self,
                "Lỗi",
                "Không thể tạo backup. Vui lòng kiểm tra log."
            )
    
    def _on_restore(self) -> None:
        """Xử lý sự kiện restore từ backup."""
        backup_dir = self.backup_service.backup_dir
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file backup để khôi phục",
            str(backup_dir),
            "Database Files (*.db)"
        )
        
        if not file_path:
            return
        
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc chắn muốn khôi phục từ backup này?\n"
            "Dữ liệu hiện tại sẽ bị ghi đè.\n\n"
            "Lưu ý: Database hiện tại sẽ được backup trước khi restore.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.backup_service.restore_from_backup(Path(file_path))
            
            if success:
                QMessageBox.information(
                    self,
                    "Thành công",
                    "Khôi phục thành công!\n\nVui lòng khởi động lại ứng dụng."
                )
                self.close()
            else:
                QMessageBox.warning(
                    self,
                    "Lỗi",
                    "Không thể khôi phục. Vui lòng kiểm tra log."
                )
    
    def _on_about(self) -> None:
        """Hiển thị thông tin về ứng dụng."""
        about_text = """
        <h2>Quản lý Sổ Công Nợ</h2>
        <p>Version 1.0.0</p>
        <p>Ứng dụng desktop quản lý sổ công nợ đơn giản.</p>
        <p><b>Tính năng:</b></p>
        <ul>
            <li>Quản lý khách hàng</li>
            <li>Ghi nhận cho vay/thu nợ</li>
            <li>Xem lịch sử giao dịch</li>
            <li>Tự động backup database</li>
        </ul>
        <p><b>Kiến trúc:</b> Clean Architecture với phân lớp rõ ràng</p>
        <p><b>Framework:</b> PySide6 (Qt for Python)</p>
        """
        
        QMessageBox.about(self, "Giới thiệu", about_text)
    
    def showEvent(self, event) -> None:
        """Override showEvent để cập nhật status bar khi window hiển thị."""
        super().showEvent(event)
        self.update_status_bar()
    
    def closeEvent(self, event) -> None:
        """Override closeEvent để confirm trước khi thoát."""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc chắn muốn thoát?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
