# ============================================================
#  helpers.py - Hàm tiện ích dùng chung cho Selenium Auto Test
#  Module: Chatbot AI Auto Test
# ============================================================

from selenium.webdriver.support.ui import WebDriverWait
from config import WAIT_TIMEOUT


def wait(driver, timeout=WAIT_TIMEOUT):
    """Trả về đối tượng WebDriverWait với timeout tuỳ chỉnh."""
    return WebDriverWait(driver, timeout)

