"""
Dịch vụ tự động backup database.

Module này cung cấp tính năng backup tự động và khôi phục database.
"""
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from core.paths import get_database_path, get_backup_dir


logger = logging.getLogger(__name__)


class BackupService:
    """
    Quản lý backup và restore database.
    
    Tự động backup database theo định kỳ và giữ tối đa 30 bản backup.
    """
    
    def __init__(self) -> None:
        """Khởi tạo backup service."""
        self.db_path = get_database_path()
        self.backup_dir = get_backup_dir()
        self.max_backups = 30
    
    def _get_backup_filename(self) -> str:
        """
        Tạo tên file backup với timestamp.
        
        Returns:
            str: Tên file backup dạng socongno_backup_YYYYMMDD_HHMMSS.db
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"socongno_backup_{timestamp}.db"
    
    def backup_now(self) -> Optional[Path]:
        """
        Thực hiện backup database ngay lập tức.
        
        Returns:
            Optional[Path]: Đường dẫn đến file backup nếu thành công, None nếu thất bại
        """
        if not self.db_path.exists():
            logger.warning(f"Database không tồn tại: {self.db_path}")
            return None
        
        try:
            backup_filename = self._get_backup_filename()
            backup_path = self.backup_dir / backup_filename
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Backup thành công: {backup_path}")
            
            # Xóa các backup cũ
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Lỗi khi backup database: {e}")
            return None
    
    def _cleanup_old_backups(self) -> None:
        """
        Xóa các backup cũ, chỉ giữ lại tối đa max_backups bản mới nhất.
        """
        try:
            # Lấy danh sách tất cả backup files
            backup_files = sorted(
                self.backup_dir.glob("socongno_backup_*.db"),
                key=lambda p: p.stat().st_mtime,
                reverse=True  # Mới nhất trước
            )
            
            # Xóa các backup cũ
            for backup_file in backup_files[self.max_backups:]:
                backup_file.unlink()
                logger.info(f"Đã xóa backup cũ: {backup_file}")
                
        except Exception as e:
            logger.error(f"Lỗi khi cleanup backup cũ: {e}")
    
    def get_backup_list(self) -> List[Path]:
        """
        Lấy danh sách tất cả các backup files.
        
        Returns:
            List[Path]: Danh sách đường dẫn backup, sắp xếp từ mới nhất
        """
        backup_files = sorted(
            self.backup_dir.glob("socongno_backup_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return backup_files
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """
        Khôi phục database từ file backup.
        
        Args:
            backup_path: Đường dẫn đến file backup
            
        Returns:
            bool: True nếu restore thành công, False nếu thất bại
        """
        if not backup_path.exists():
            logger.error(f"File backup không tồn tại: {backup_path}")
            return False
        
        try:
            # Backup database hiện tại trước khi restore
            if self.db_path.exists():
                safety_backup = self.backup_dir / f"pre_restore_{self._get_backup_filename()}"
                shutil.copy2(self.db_path, safety_backup)
                logger.info(f"Đã tạo safety backup: {safety_backup}")
            
            # Copy backup file đè lên database hiện tại
            shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Restore database thành công từ: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi restore database: {e}")
            return False
    
    def auto_backup_if_needed(self) -> Optional[Path]:
        """
        Tự động backup nếu chưa có backup trong ngày hôm nay.
        
        Returns:
            Optional[Path]: Đường dẫn đến file backup nếu được tạo, None nếu không cần hoặc thất bại
        """
        # Kiểm tra xem đã có backup trong ngày hôm nay chưa
        today = datetime.now().date()
        backup_files = self.get_backup_list()
        
        for backup_file in backup_files:
            # Parse timestamp từ tên file
            try:
                # Format: socongno_backup_YYYYMMDD_HHMMSS.db
                parts = backup_file.stem.split('_')
                if len(parts) >= 3:
                    date_str = parts[2]  # YYYYMMDD
                    backup_date = datetime.strptime(date_str, "%Y%m%d").date()
                    
                    if backup_date == today:
                        logger.info("Đã có backup trong ngày hôm nay, không cần backup lại")
                        return None
            except (ValueError, IndexError):
                continue
        
        # Chưa có backup hôm nay, tạo backup mới
        logger.info("Chưa có backup hôm nay, đang tạo backup tự động...")
        return self.backup_now()
