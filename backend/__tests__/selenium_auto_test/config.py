# ============================================================
#  config.py - Cấu hình chung cho toàn bộ Selenium Auto Test
#  Usecase: UC Xử lý đơn hàng
# ============================================================

# URL Frontend (Vite dev server)
BASE_URL = "http://localhost:5173"

# Cấu hình kết nối MySQL Database (Dùng để rollback dữ liệu sau khi test)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "ecommerce_db",
}

# Tài khoản Admin để đăng nhập
ADMIN_EMAIL    = "admin@example.com"
ADMIN_PASSWORD = "Admin@123456"

# Thời gian chờ mặc định (giây) cho WebDriverWait
WAIT_TIMEOUT = 15

# Order ID dùng để test (cần tồn tại trong DB và ở trạng thái phù hợp)
# Kịch bản 1: cần order ở trạng thái 'confirmed' (Đã xác nhận)
ORDER_ID_SCENARIO_1 = 2

# Kịch bản 2: cần order COD ở trạng thái payment 'unpaid' (Chưa thanh toán)
ORDER_ID_SCENARIO_2 = 3

# Kịch bản 3: cần order ở trạng thái 'pending' hoặc 'confirmed'
ORDER_ID_SCENARIO_3 = 4

# Thông tin vận đơn sẽ điền vào form (Kịch bản 1)
TRACKING_NUMBER = "VN-AUTO-2026"
CARRIER         = "GHN"
SHIPPED_DATE    = "2026-07-21"   # định dạng YYYY-MM-DD (dùng cho input type=date)
