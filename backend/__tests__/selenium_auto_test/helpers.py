# ============================================================
#  helpers.py - Hàm tiện ích dùng chung cho tất cả kịch bản
#  Usecase: UC Xử lý đơn hàng
# ============================================================

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from config import BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD, WAIT_TIMEOUT


def wait(driver, timeout=WAIT_TIMEOUT):
    """Trả về đối tượng WebDriverWait với timeout tuỳ chỉnh."""
    return WebDriverWait(driver, timeout)


def human_select_by_value(element, value):
    """
    Bắt chước thao tác người dùng: Click xổ danh sách -> chờ 1s -> Click chọn option.
    """
    element.click()
    time.sleep(1) # Chờ 1 giây để mắt người kịp nhìn thấy danh sách xổ xuống
    option = element.find_element(By.CSS_SELECTOR, f"option[value='{value}']")
    option.click()
    time.sleep(0.5) # Chờ một chút sau khi click chọn xong


def login_as_admin(driver):
    """
    Thực hiện đăng nhập tài khoản Admin.
    - Điều hướng đến /auth/login
    - Nhập email + password
    - Nhấn Submit
    - Chờ redirect về /admin/dashboard
    """
    driver.get(f"{BASE_URL}/auth/login")

    # Chờ form đăng nhập xuất hiện
    email_input = wait(driver).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
    )
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

    # Xoá dữ liệu cũ (nếu có) và nhập thông tin đăng nhập
    email_input.clear()
    email_input.send_keys(ADMIN_EMAIL)
    password_input.clear()
    password_input.send_keys(ADMIN_PASSWORD)

    # Click nút Đăng nhập
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()

    # Chờ redirect về trang admin dashboard
    wait(driver).until(EC.url_contains("/admin/dashboard"))
    print(f"  [LOGIN] Đăng nhập Admin thành công → {driver.current_url}")


def navigate_to_orders(driver):
    """
    Điều hướng đến trang Quản lý đơn hàng (/admin/orders).
    Chờ bảng danh sách đơn hàng (admin-table) xuất hiện.
    """
    driver.get(f"{BASE_URL}/admin/orders")
    wait(driver).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.admin-table"))
    )
    print(f"  [NAV] Đã vào trang Quản lý đơn hàng → {driver.current_url}")


def find_order_row_by_id(driver, order_id):
    """
    Tìm row của đơn hàng có ID = order_id trong bảng.
    Trả về WebElement của thẻ <tr> tương ứng.
    Raise ValueError nếu không tìm thấy.
    """
    rows = driver.find_elements(By.CSS_SELECTOR, "table.admin-table tbody tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells and cells[0].text.strip() == str(order_id):
            return row
    raise ValueError(f"Không tìm thấy đơn hàng có ID={order_id} trong bảng!")


def get_status_select_in_row(driver, row, order_id):
    """
    Lấy thẻ <select> trạng thái đơn trong một row.
    Dùng aria-label="Trạng thái đơn {order_id}" theo code Orders.jsx.
    """
    return wait(driver).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"select[aria-label='Trạng thái đơn {order_id}']")
        )
    )


def get_payment_select_in_row(driver, order_id):
    """
    Lấy thẻ <select> trạng thái thanh toán theo aria-label.
    Dùng aria-label="Trạng thái thanh toán {order_id}" theo code Orders.jsx.
    """
    return wait(driver).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"select[aria-label='Trạng thái thanh toán {order_id}']")
        )
    )


def wait_for_shipment_modal(driver):
    """
    Chờ Popup ShipmentModal hiển thị.
    Điều kiện: input có name='tracking_number' visible.
    Trả về WebElement của input tracking_number.
    """
    tracking_input = wait(driver).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='tracking_number']"))
    )
    print("  [MODAL] Popup Xác nhận giao hàng đã xuất hiện.")
    return tracking_input


def wait_for_shipment_modal_closed(driver):
    """
    Chờ Popup ShipmentModal đóng lại.
    Điều kiện: input tracking_number biến mất khỏi DOM.
    """
    wait(driver).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "input[name='tracking_number']"))
    )
    print("  [MODAL] Popup đã đóng thành công.")


def fill_shipment_form(driver, tracking_number, carrier, shipped_date):
    """
    Điền đầy đủ thông tin vào form ShipmentModal:
    - Mã vận đơn (tracking_number)
    - Nhà vận chuyển (carrier) - dùng Select
    - Ngày gửi hàng (shipped_date) - định dạng YYYY-MM-DD

    Lưu ý: Dùng JavaScript để set value cho input[type=date]
    vì Selenium không hỗ trợ trực tiếp trên một số hệ điều hành.
    """
    # Điền Mã vận đơn
    tracking_input = driver.find_element(By.CSS_SELECTOR, "input[name='tracking_number']")
    tracking_input.clear()
    tracking_input.send_keys(tracking_number)
    print(f"  [FORM] Đã nhập Mã vận đơn: {tracking_number}")

    # Chọn Nhà vận chuyển (mô phỏng thao tác click thật)
    carrier_select_el = driver.find_element(By.CSS_SELECTOR, "select[name='carrier']")
    human_select_by_value(carrier_select_el, carrier)
    print(f"  [FORM] Đã chọn Nhà vận chuyển: {carrier}")

    # Điền Ngày gửi hàng (Dùng native setter để React nhận diện được sự thay đổi)
    date_input = driver.find_element(By.CSS_SELECTOR, "input[name='shipped_date']")
    driver.execute_script("""
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(arguments[0], arguments[1]);
        var ev = new Event('input', { bubbles: true });
        arguments[0].dispatchEvent(ev);
    """, date_input, shipped_date)
    print(f"  [FORM] Đã nhập Ngày gửi hàng: {shipped_date}")


def click_save_shipment(driver):
    """Click nút Lưu trong ShipmentModal."""
    save_btn = driver.find_element(
        By.XPATH,
        "//button[@type='submit' and contains(text(),'Lưu')]"
    )
    save_btn.click()
    print("  [FORM] Đã click nút Lưu.")
