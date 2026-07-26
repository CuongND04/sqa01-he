# Sử dụng image MySQL 8.0 chính thức làm base image
FROM mysql:8.0

# Thiết lập ngôn ngữ/múi giờ (tùy chọn)
ENV TZ=Asia/Ho_Chi_Minh

# Cấu hình MySQL để dùng UTF-8 đầy đủ cho tiếng Việt
RUN echo "[mysqld]\ncharacter-set-server=utf8mb4\ncollation-server=utf8mb4_unicode_ci\nskip-character-set-client-handshake\n" > /etc/mysql/conf.d/charset.cnf

# Sao chép file script SQL khởi tạo dữ liệu vào thư mục tự động chạy của container
# Bất kỳ file .sql nào trong thư mục này sẽ tự động được chạy khi container được khởi tạo lần đầu
COPY ./ecommerce_db.sql /docker-entrypoint-initdb.d/01_init.sql
