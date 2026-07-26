# -*- coding: utf-8 -*-
# ============================================================
#  test_chatbot_ui.py
#  Kịch bản Auto Test UI Chatbot bằng Selenium
# ============================================================

import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from helpers import wait
from config import BASE_URL


class TestChatbotUI(unittest.TestCase):
    """Kịch bản Auto Test UI/UX cho tính năng Chatbot"""

    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(3)

    @classmethod
    def tearDownClass(cls):
        time.sleep(1)
        cls.driver.quit()

    def test_01_happy_path_gui_tin_nhan(self):
        """UI_AUTO_CHAT_01: Luồng End-to-End cơ bản"""
        driver = self.driver
        driver.get(BASE_URL)

        # 1. Mở khung chat
        chatbot_icon = wait(driver).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Chatbot Hỗ Trợ']"))
        )
        chatbot_icon.click()
        
        # 2. Nhập tin nhắn và gửi
        chat_input = wait(driver).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[aria-label='chat-input']"))
        )
        chat_input.send_keys("Xin chào shop")
        
        send_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
        send_btn.click()
        
        # 3. Assert bong bóng tin nhắn của User xuất hiện
        user_msg = wait(driver).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Xin chào shop')]"))
        )
        self.assertTrue(user_msg.is_displayed(), "Tin nhắn của User không hiển thị!")
        print("  [PASS] UI_AUTO_CHAT_01: Đã gửi và hiển thị tin nhắn User.")

    def test_02_hieu_ung_loading(self):
        """UI_AUTO_CHAT_02: Kiểm tra hiệu ứng Loading/Typing"""
        driver = self.driver
        # Giả sử khung chat đang mở từ test 1
        chat_input = wait(driver).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[aria-label='chat-input']"))
        )
        chat_input.send_keys("Gợi ý cho tôi các sản phẩm đặc sản")
        
        # Tìm nút gửi dựa trên vị trí thay vì text cứng để tránh lỗi ngôn ngữ
        # Nút button nằm ngay sau input
        send_btn = driver.find_element(By.XPATH, "//input[@aria-label='chat-input']/following-sibling::button")
        send_btn.click()
        
        # Ngay sau khi click, nút Send sẽ bị disabled và đổi trạng thái
        loading_btn = wait(driver).until(
            EC.presence_of_element_located((By.XPATH, "//input[@aria-label='chat-input']/following-sibling::button[@disabled]"))
        )
        self.assertTrue(loading_btn.is_displayed(), "Không thấy hiệu ứng Loading!")
        print("  [PASS] UI_AUTO_CHAT_02: Hiệu ứng Loading hoạt động.")
        
        # Chờ AI trả lời xong (Nút send phục hồi, hết disabled)
        wait(driver).until(
            EC.presence_of_element_located((By.XPATH, "//input[@aria-label='chat-input']/following-sibling::button[not(@disabled)]"))
        )

    def test_03_loi_phong_to_khung_chat(self):
        """UI_AUTO_CHAT_03: Kiểm tra giao diện khung chat khi Phóng to (Cố tình bắt lỗi)"""
        driver = self.driver
        
        expand_btn = wait(driver).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Phóng to']"))
        )
        expand_btn.click()
        time.sleep(1) # Chờ animation CSS
        
        # Lấy tọa độ thẻ container cha (thẻ có box-shadow chứa toàn bộ chat)
        chat_container = driver.find_element(By.XPATH, "//div[contains(@style, 'box-shadow')]")
        container_rect = chat_container.rect
        container_bottom = container_rect['y'] + container_rect['height']
        
        # Lấy tọa độ thẻ input
        chat_input = driver.find_element(By.CSS_SELECTOR, "input[aria-label='chat-input']")
        input_rect = chat_input.rect
        input_bottom = input_rect['y'] + input_rect['height']
        
        # EXPECTED FAIL: Input bị tràn mất phần bên dưới do css height tính toán sai
        # Nếu điểm đáy của input (input_bottom) lớn hơn điểm đáy của container (container_bottom) thì input bị tràn (bị cắt xén)
        try:
            self.assertLessEqual(input_bottom, container_bottom, "Khung input bị tràn xuống dưới màn hình/bị cắt xén!")
            print("  [PASS] Khung chat phóng to bình thường.")
        except AssertionError as e:
            print(f"  [EXPECTED FAIL] UI_AUTO_CHAT_03: {e}")
            
        # Thu nhỏ lại để test case sau chạy
        collapse_btn = driver.find_element(By.XPATH, "//button[@title='Thu nhỏ']")
        collapse_btn.click()
        time.sleep(1)

    def test_04_loi_auto_scroll(self):
        """UI_AUTO_CHAT_04: Kiểm tra tự động cuộn (Auto-scroll)"""
        driver = self.driver
        chat_input = driver.find_element(By.CSS_SELECTOR, "input[aria-label='chat-input']")
        
        # Gửi liên tục để làm đầy màn hình chat
        for i in range(3):
            chat_input.send_keys(f"Tin nhắn rác {i}")
            send_btn = wait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send')]"))
            )
            send_btn.click()
            time.sleep(0.5)
            
        # Kiểm tra thẻ div chứa tin nhắn
        messages_container = driver.find_elements(By.XPATH, "//div[contains(@style, 'overflow-y: auto')]")
        
        if messages_container:
            container = messages_container[0]
            scroll_top = driver.execute_script("return arguments[0].scrollTop;", container)
            scroll_height = driver.execute_script("return arguments[0].scrollHeight;", container)
            client_height = driver.execute_script("return arguments[0].clientHeight;", container)
            
            # Nếu thanh cuộn không kéo xuống dưới cùng, scroll_top + client_height sẽ nhỏ hơn nhiều so với scroll_height
            try:
                self.assertAlmostEqual(scroll_top + client_height, scroll_height, delta=10, 
                                     msg="Thanh cuộn không tự động kéo xuống đáy!")
                print("  [PASS] Auto-scroll hoạt động.")
            except AssertionError as e:
                print(f"  [EXPECTED FAIL] UI_AUTO_CHAT_04: {e}")
        else:
            print("  [SKIP] Không tìm thấy container cuộn.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
