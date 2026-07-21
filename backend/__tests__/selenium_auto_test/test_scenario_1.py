# -*- coding: utf-8 -*-
# ============================================================
#  test_scenario_1.py
#  Kich ban 1: Cap nhat trang thai don -> "Dang Giao" + Tao van don
#  Pham vi: TC_SHIP_035, TC_SHIP_008, TC_ORDER_021
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

from config import ORDER_ID_SCENARIO_1, TRACKING_NUMBER, CARRIER, SHIPPED_DATE
from helpers import (
    wait, login_as_admin, navigate_to_orders,
    find_order_row_by_id, get_status_select_in_row,
    wait_for_shipment_modal, wait_for_shipment_modal_closed,
    fill_shipment_form, click_save_shipment,
)


class TestScenario1(unittest.TestCase):
    """Kich ban 1: Cap nhat trang thai don + Tao van don"""

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

    def test_kich_ban_1_cap_nhat_trang_thai_don_va_tao_van_don(self):
        """
        [KC1] Cap nhat trang thai don -> Dang Giao va tao van don qua ShipmentModal
        Assert 1: Popup dong sau khi Luu (TC_SHIP_008)
        Assert 2: Badge trang thai = 'shipping' (TC_ORDER_021)
        Assert 3: Nut 'Quan ly giao van' xuat hien (TC_SHIP_035)
        """
        driver = self.driver

        # Buoc 1: Dang nhap Admin
        login_as_admin(driver)
        self.assertIn("/admin/dashboard", driver.current_url, "Dang nhap that bai")

        # Buoc 2: Mo trang Quan ly don hang
        navigate_to_orders(driver)
        self.assertIn("/admin/orders", driver.current_url)

        # Buoc 3+4: Tim order va chuyen trang thai sang 'shipping'
        row = find_order_row_by_id(driver, ORDER_ID_SCENARIO_1)
        status_el = get_status_select_in_row(driver, row, ORDER_ID_SCENARIO_1)
        current = status_el.get_attribute("value")
        print(f"\n  [INFO] Trang thai hien tai order {ORDER_ID_SCENARIO_1}: {current}")

        if current == "shipping":
            # Da o 'shipping' -> click nut Quan ly giao van truc tiep
            btn = wait(driver).until(EC.element_to_be_clickable((
                By.XPATH,
                f"//tr[td[1][normalize-space()='{ORDER_ID_SCENARIO_1}']]"
                f"//button[contains(text(),'Qu\u1ea3n l\u00fd giao v\u1eadn')]"
            )))
            btn.click()
            print("  [ACTION] Click nut 'Quan ly giao van'.")
        else:
            Select(status_el).select_by_value("shipping")
            print("  [ACTION] Chon 'shipping' tu dropdown.")

        # Buoc 5: Cho Popup ShipmentModal xuat hien
        tracking_input = wait_for_shipment_modal(driver)
        self.assertTrue(tracking_input.is_displayed(), "ShipmentModal khong hien ra!")

        # Buoc 6+7: Dien form va click Luu
        fill_shipment_form(driver, TRACKING_NUMBER, CARRIER, SHIPPED_DATE)
        click_save_shipment(driver)

        # Assert 1: Popup phai tu dong dong (TC_SHIP_008)
        wait_for_shipment_modal_closed(driver)
        modals = driver.find_elements(By.CSS_SELECTOR, "input[name='tracking_number']")
        self.assertTrue(
            len(modals) == 0 or not modals[0].is_displayed(),
            "Assert 1 FAIL: Popup ShipmentModal van con hien!"
        )
        print("  [PASS] Assert 1: Popup da dong. (TC_SHIP_008)")

        # Assert 2: Badge trang thai = 'shipping' (TC_ORDER_021)
        time.sleep(1)
        status_el2 = wait(driver).until(EC.presence_of_element_located((
            By.CSS_SELECTOR, f"select[aria-label='Tr\u1ea1ng th\u00e1i \u0111\u01a1n {ORDER_ID_SCENARIO_1}']"
        )))
        self.assertEqual(status_el2.get_attribute("value"), "shipping",
                         "Assert 2 FAIL: Badge trang thai khong phai 'shipping'!")
        print("  [PASS] Assert 2: Badge = 'shipping' (Dang giao). (TC_ORDER_021)")

        # Assert 3: Nut 'Quan ly giao van' phai xuat hien (TC_SHIP_035)
        row2 = find_order_row_by_id(driver, ORDER_ID_SCENARIO_1)
        btns = row2.find_elements(By.XPATH, ".//button[contains(text(),'Qu\u1ea3n l\u00fd giao v\u1eadn')]")
        self.assertTrue(len(btns) > 0 and btns[0].is_displayed(),
                        "Assert 3 FAIL: Nut 'Quan ly giao van' khong xuat hien!")
        print("  [PASS] Assert 3: Nut 'Quan ly giao van' da hien. (TC_SHIP_035)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
