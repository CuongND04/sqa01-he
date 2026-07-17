# Sử dụng image MySQL 8.0 chính thức làm base image
FROM mysql:8.0

# Thiết lập ngôn ngữ/múi giờ (tùy chọn)
ENV TZ=Asia/Ho_Chi_Minh

# Sao chép file script SQL khởi tạo dữ liệu vào thư mục tự động chạy của container
# Bất kỳ file .sql nào trong thư mục này sẽ tự động được chạy khi container được khởi tạo lần đầu
COPY ./ecommerce_db.sql /docker-entrypoint-initdb.d/01_init.sql
