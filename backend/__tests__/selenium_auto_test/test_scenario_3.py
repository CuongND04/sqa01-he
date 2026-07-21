# -*- coding: utf-8 -*-
# ============================================================
#  test_scenario_3.py
#  Kich ban 3: Huy don hang + Kiem tra logic UI an nut
#  Pham vi: TC_ORDER_022, TC_ORDER_026, TC_SHIP_039
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

from config import ORDER_ID_SCENARIO_3
from helpers import (
    wait, login_as_admin, navigate_to_orders,
    find_order_row_by_id, get_status_select_in_row,
)


class TestScenario3(unittest.TestCase):
    """Kich ban 3: Huy don hang va kiem tra UI an nut"""

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

    def test_kich_ban_3_huy_don_hang_va_kiem_tra_UI(self):
        """
        [KC3] Huy don hang va kiem tra logic UI
        Assert 1: Badge trang thai = 'canceled' (TC_ORDER_022)
        Assert 2: Nut 'Quan ly giao van' bi xoa khoi DOM (TC_ORDER_026, TC_SHIP_039)
        """
        driver = self.driver

        # Buoc 1: Dang nhap Admin
        login_as_admin(driver)
        self.assertIn("/admin/dashboard", driver.current_url, "Dang nhap that bai")

        # Buoc 2: Mo trang Quan ly don hang
        navigate_to_orders(driver)
        self.assertIn("/admin/orders", driver.current_url)

        # Buoc 3: Tim order
        row = find_order_row_by_id(driver, ORDER_ID_SCENARIO_3)
        status_el = get_status_select_in_row(driver, row, ORDER_ID_SCENARIO_3)
        current = status_el.get_attribute("value")
        print(f"\n  [INFO] Trang thai hien tai order {ORDER_ID_SCENARIO_3}: {current}")

        # Buoc 4+5: Chon 'canceled'
        Select(status_el).select_by_value("canceled")
        print("  [ACTION] Chon 'canceled' tu dropdown Trang thai don.")
        time.sleep(2)

        # Assert 1: Badge = 'canceled' (TC_ORDER_022)
        status_el2 = wait(driver).until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            f"select[aria-label='Tr\u1ea1ng th\u00e1i \u0111\u01a1n {ORDER_ID_SCENARIO_3}']"
        )))
        self.assertEqual(status_el2.get_attribute("value"), "canceled",
                         "Assert 1 FAIL: Badge trang thai khong phai 'canceled'!")
        print("  [PASS] Assert 1: Badge = 'canceled' (Da huy). (TC_ORDER_022)")

        # Assert 2: Nut 'Quan ly giao van' bi xoa khoi DOM (TC_ORDER_026, TC_SHIP_039)
        row2 = find_order_row_by_id(driver, ORDER_ID_SCENARIO_3)
        btns = row2.find_elements(
            By.XPATH, ".//button[contains(text(),'Qu\u1ea3n l\u00fd giao v\u1eadn')]"
        )
        self.assertEqual(len(btns), 0,
                         f"Assert 2 FAIL: Van con {len(btns)} nut 'Quan ly giao van' tren row da huy!")
        print("  [PASS] Assert 2: findElements().size()==0. Nut da bi xoa khoi DOM. (TC_ORDER_026)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
