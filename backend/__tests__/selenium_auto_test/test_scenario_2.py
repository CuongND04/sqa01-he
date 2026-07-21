# -*- coding: utf-8 -*-
# ============================================================
#  test_scenario_2.py
#  Kich ban 2: Cap nhat trang thai Thanh toan COD -> Da Thanh Toan
#  Pham vi: TC_PAY_008, TC_PAY_015, TC_PAY_003
# ============================================================

import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import ORDER_ID_SCENARIO_2
from helpers import (
    wait, login_as_admin, navigate_to_orders,
    find_order_row_by_id, get_payment_select_in_row,
)


class TestScenario2(unittest.TestCase):
    """Kich ban 2: Cap nhat trang thai Thanh toan COD"""

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

    def test_kich_ban_2_cap_nhat_trang_thai_thanh_toan(self):
        """
        [KC2] Cap nhat trang thai thanh toan COD: unpaid -> paid
        Assert 1: Badge thanh toan = 'paid' (TC_PAY_008, TC_PAY_015)
        Assert 2: Mau nen xanh la + text 'Da Thanh Toan' (TC_PAY_003)
        """
        driver = self.driver

        # Buoc 1: Dang nhap Admin
        login_as_admin(driver)
        self.assertIn("/admin/dashboard", driver.current_url, "Dang nhap that bai")

        # Buoc 2: Mo trang Quan ly don hang
        navigate_to_orders(driver)
        self.assertIn("/admin/orders", driver.current_url)

        # Buoc 3: Tim order COD
        row = find_order_row_by_id(driver, ORDER_ID_SCENARIO_2)
        pay_el = get_payment_select_in_row(driver, ORDER_ID_SCENARIO_2)
        current = pay_el.get_attribute("value")
        print(f"\n  [INFO] Trang thai thanh toan hien tai order {ORDER_ID_SCENARIO_2}: {current}")

        # Buoc 4+5: Chon 'paid'
        Select(pay_el).select_by_value("paid")
        print("  [ACTION] Chon 'paid' tu dropdown Thanh toan.")
        time.sleep(2)

        # Assert 1: Badge = 'paid' (TC_PAY_008, TC_PAY_015)
        pay_el2 = wait(driver).until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            f"select[aria-label='Tr\u1ea1ng th\u00e1i thanh to\u00e1n {ORDER_ID_SCENARIO_2}']"
        )))
        self.assertEqual(pay_el2.get_attribute("value"), "paid",
                         "Assert 1 FAIL: Badge thanh toan khong phai 'paid'!")
        print("  [PASS] Assert 1: Badge = 'paid'. (TC_PAY_008, TC_PAY_015)")

        # Assert 2: Mau nen xanh la + text dung (TC_PAY_003)
        bg = pay_el2.value_of_css_property("background-color")
        green_ok = ["rgba(236, 253, 245, 1)", "rgb(236, 253, 245)"]
        self.assertIn(bg, green_ok,
                      f"Assert 2 FAIL: Mau nen Badge la '{bg}', ky vong xanh la!")
        text = Select(pay_el2).first_selected_option.text
        self.assertIn("thanh to\u00e1n", text.lower(),
                      f"Assert 2 FAIL: Text Badge la '{text}'!")
        print(f"  [PASS] Assert 2: Mau = '{bg}', text = '{text}'. (TC_PAY_003)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
