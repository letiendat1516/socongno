# Quản lý Sổ Công Nợ

## Giới thiệu

Ứng dụng desktop quản lý sổ công nợ đơn giản, được xây dựng với PySide6 (Qt for Python) theo kiến trúc Clean Architecture.

## Tính năng

- ✅ **Quản lý khách hàng**: Thêm, sửa, xóa thông tin khách hàng
- ✅ **Ghi nhận cho vay/thu nợ**: Theo dõi các khoản cho vay và thu nợ
- ✅ **Xem lịch sử giao dịch**: Xem chi tiết lịch sử giao dịch của từng khách hàng
- ✅ **Tự động backup**: Database được tự động backup mỗi ngày
- ✅ **Khôi phục dữ liệu**: Khôi phục database từ các bản backup

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- Windows, macOS, hoặc Linux

### Các bước cài đặt

1. Clone repository:
```bash
git clone https://github.com/letiendat1516/socongno.git
cd socongno
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python main.py
```

## Cấu trúc dự án

```
socongno/
│
├── main.py                    # Entry point của ứng dụng
│
├── core/                      # Hạ tầng hệ thống
│   ├── database.py            # Quản lý SQLite database
│   ├── migrations.py          # Quản lý database versioning
│   ├── backup_service.py      # Dịch vụ backup tự động
│   └── paths.py               # Quản lý đường dẫn AppData
│
├── models/                    # Data models (entities)
│   ├── customer.py            # Model cho khách hàng
│   └── transaction.py         # Model cho giao dịch
│
├── repositories/              # Data access layer
│   ├── customer_repo.py       # Repository cho customers
│   └── transaction_repo.py    # Repository cho transactions
│
├── services/                  # Business logic layer
│   └── debt_service.py        # Service xử lý logic công nợ
│
├── controllers/               # Controller layer
│   └── customer_controller.py # Controller cho customers
│
└── views/                     # Presentation layer (UI)
    ├── main_window.py         # Cửa sổ chính
    └── customer_screen.py     # Màn hình quản lý khách hàng
```

## Kiến trúc

Ứng dụng được xây dựng theo **Clean Architecture** với phân lớp rõ ràng:

```
View → Controller → Service → Repository → Database
```

- **View**: Giao diện người dùng (PySide6)
- **Controller**: Xử lý events từ UI, điều phối các thao tác
- **Service**: Business logic và validation rules
- **Repository**: Truy xuất dữ liệu từ database (SQL queries)
- **Database**: SQLite database

### Nguyên tắc thiết kế

- ✅ Separation of Concerns: Mỗi layer có trách nhiệm riêng biệt
- ✅ Dependency Inversion: Layers không phụ thuộc trực tiếp vào implementation
- ✅ Single Responsibility: Mỗi class có một mục đích duy nhất
- ✅ Type Hints: Đầy đủ type hints cho tất cả functions và methods
- ✅ Error Handling: Xử lý lỗi đúng cách với try/except và logging

## Lưu trữ dữ liệu

Database và backups được lưu tại:

- **Windows**: `%APPDATA%\SoCongNo\`
- **macOS**: `~/Library/Application Support/SoCongNo/`
- **Linux**: `~/.local/share/SoCongNo/`

### Cấu trúc database

**Bảng `customers`**:
- `id`: INTEGER PRIMARY KEY
- `name`: TEXT (tên khách hàng)
- `phone`: TEXT (số điện thoại)
- `address`: TEXT (địa chỉ)
- `created_at`: TEXT (thời gian tạo)

**Bảng `transactions`**:
- `id`: INTEGER PRIMARY KEY
- `customer_id`: INTEGER (khóa ngoại đến customers)
- `amount`: REAL (số tiền)
- `transaction_type`: TEXT (CHO_VAY hoặc THU_NO)
- `note`: TEXT (ghi chú)
- `created_at`: TEXT (thời gian tạo)

## Backup & Restore

- Backup tự động chạy mỗi ngày khi khởi động ứng dụng
- Tối đa 30 bản backup được giữ lại, các backup cũ hơn sẽ tự động bị xóa
- Có thể backup thủ công qua menu: `File → Backup ngay`
- Khôi phục từ backup: `File → Khôi phục từ backup`

## Screenshot

*(Placeholder - sẽ cập nhật sau khi chạy ứng dụng)*

## Phát triển thêm

### Thêm migration mới

Để thêm migration cho database schema, chỉnh sửa file `core/migrations.py`:

1. Thêm method migration mới (ví dụ: `_migration_2_add_email_field`)
2. Thêm vào danh sách `migrations` trong `apply_migrations()`

### Mở rộng tính năng

Các tính năng có thể mở rộng:

- Export/Import dữ liệu (Excel, CSV)
- Báo cáo thống kê
- Quản lý nhiều loại công nợ
- Thông báo nhắc nợ
- Tìm kiếm nâng cao

## License

MIT License

## Tác giả

Phát triển bởi [letiendat1516](https://github.com/letiendat1516)
