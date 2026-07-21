# -*- coding: utf-8 -*-
# ============================================================
#  run_all.py
#  Chay tat ca 3 kich ban trong 1 cua so Chrome duy nhat
#  Mo Chrome 1 lan -> KC1 -> KC2 -> KC3 -> Dong Chrome
# ============================================================

import sys
import io
import time
import unittest
import mysql.connector

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import DB_CONFIG, ORDER_ID_SCENARIO_1, ORDER_ID_SCENARIO_2, ORDER_ID_SCENARIO_3
from config import TRACKING_NUMBER, CARRIER, SHIPPED_DATE
from helpers import (
    wait, login_as_admin, navigate_to_orders,
    find_order_row_by_id, get_status_select_in_row, get_payment_select_in_row,
    wait_for_shipment_modal, wait_for_shipment_modal_closed,
    fill_shipment_form, click_save_shipment, human_select_by_value
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC


class AllScenarios(unittest.TestCase):
    """
    Chay ca 3 kich ban trong 1 cua so Chrome duy nhat.
    setUpClass: Mo Chrome 1 lan.
    tearDownClass: Dong Chrome 1 lan.
    """

    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(3)
        print("\n[SETUP] Da mo Chrome. Bat dau chay 3 kich ban...\n")

    @classmethod
    def tearDownClass(cls):
        time.sleep(1)
        cls.driver.quit()
        print("\n[TEARDOWN] Da dong Chrome.")

        # Thuc hien Rollback Database (Cach 1)
        print("[ROLLBACK] Dang khoi phuc du lieu trong Database...")
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Rollback Scenario 1
            cursor.execute(f"UPDATE orders SET status = 'confirmed' WHERE id = {ORDER_ID_SCENARIO_1}")
            cursor.execute(f"DELETE FROM shipments WHERE tracking_number = '{TRACKING_NUMBER}'")

            # Rollback Scenario 2
            cursor.execute(f"UPDATE orders SET payment_status = 'unpaid' WHERE id = {ORDER_ID_SCENARIO_2}")

            # Rollback Scenario 3
            cursor.execute(f"UPDATE orders SET status = 'pending' WHERE id = {ORDER_ID_SCENARIO_3}")

            conn.commit()
            print("[ROLLBACK] Khoi phuc du lieu thanh cong! (DB da tro ve trang thai ban dau)")
        except Exception as e:
            print(f"[ROLLBACK ERROR] Loi khi khoi phuc du lieu: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    # ----------------------------------------------------------
    # KICH BAN 1: Cap nhat trang thai don + Tao van don
    # TC_SHIP_035, TC_SHIP_008, TC_ORDER_021
    # ----------------------------------------------------------
    def test_1_kich_ban_1_cap_nhat_trang_thai_va_tao_van_don(self):
        """[KC1] Cap nhat trang thai don -> Dang Giao va tao van don"""
        driver = self.driver

        login_as_admin(driver)
        self.assertIn("/admin/dashboard", driver.current_url, "KC1: Dang nhap that bai")

        navigate_to_orders(driver)

        row = find_order_row_by_id(driver, ORDER_ID_SCENARIO_1)
        status_el = get_status_select_in_row(driver, row, ORDER_ID_SCENARIO_1)
        current = status_el.get_attribute("value")
        print(f"  [INFO] Trang thai hien tai order {ORDER_ID_SCENARIO_1}: {current}")

        if current == "shipping":
            btn = wait(driver).until(EC.element_to_be_clickable((
                By.XPATH,
                f"//tr[td[1][normalize-space()='{ORDER_ID_SCENARIO_1}']]"
                f"//button[contains(text(),'Qu\u1ea3n l\u00fd giao v\u1eadn')]"
            )))
            btn.click()
        else:
            human_select_by_value(status_el, "shipping")

        tracking_input = wait_for_shipment_modal(driver)
        self.assertTrue(tracking_input.is_displayed(), "KC1 Assert: ShipmentModal khong hien!")

        fill_shipment_form(driver, TRACKING_NUMBER, CARRIER, SHIPPED_DATE)
        click_save_shipment(driver)

        wait_for_shipment_modal_closed(driver)
        modals = driver.find_elements(By.CSS_SELECTOR, "input[name='tracking_number']")
        self.assertTrue(len(modals) == 0 or not modals[0].is_displayed(),
                        "KC1 Assert 1 FAIL: Popup van con hien! (TC_SHIP_008)")
        print("  [PASS] Assert 1: Popup da dong. (TC_SHIP_008)")

        time.sleep(1)
        status_el2 = wait(driver).until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            f"select[aria-label='Tr\u1ea1ng th\u00e1i \u0111\u01a1n {ORDER_ID_SCENARIO_1}']"
        )))
        self.assertEqual(status_el2.get_attribute("value"), "shipping",
                         "KC1 Assert 2 FAIL: Badge khong phai 'shipping'! (TC_ORDER_021)")
        print("  [PASS] Assert 2: Badge = 'shipping'. (TC_ORDER_021)")

        row2 = find_order_row_by_id(driver, ORDER_ID_SCENARIO_1)
        btns = row2.find_elements(By.XPATH,
                                  ".//button[contains(text(),'Qu\u1ea3n l\u00fd giao v\u1eadn')]")
        self.assertTrue(len(btns) > 0 and btns[0].is_displayed(),
                        "KC1 Assert 3 FAIL: Nut 'Quan ly giao van' khong hien! (TC_SHIP_035)")
        print("  [PASS] Assert 3: Nut 'Quan ly giao van' da hien. (TC_SHIP_035)")

    # ----------------------------------------------------------
    # KICH BAN 2: Cap nhat trang thai Thanh toan COD
    # TC_PAY_008, TC_PAY_015, TC_PAY_003
    # ----------------------------------------------------------
    def test_2_kich_ban_2_cap_nhat_trang_thai_thanh_toan(self):
        """[KC2] Cap nhat trang thai thanh toan COD: unpaid -> paid"""
        driver = self.driver

        navigate_to_orders(driver)

        row = find_order_row_by_id(driver, ORDER_ID_SCENARIO_2)
        pay_el = get_payment_select_in_row(driver, ORDER_ID_SCENARIO_2)
        current = pay_el.get_attribute("value")
        print(f"  [INFO] Trang thai thanh toan hien tai order {ORDER_ID_SCENARIO_2}: {current}")

        human_select_by_value(pay_el, "paid")
        print("  [ACTION] Chon 'paid'.")
        time.sleep(2)

        pay_el2 = wait(driver).until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            f"select[aria-label='Tr\u1ea1ng th\u00e1i thanh to\u00e1n {ORDER_ID_SCENARIO_2}']"
        )))
        self.assertEqual(pay_el2.get_attribute("value"), "paid",
                         "KC2 Assert 1 FAIL: Badge khong phai 'paid'! (TC_PAY_008)")
        print("  [PASS] Assert 1: Badge = 'paid'. (TC_PAY_008, TC_PAY_015)")

        bg = pay_el2.value_of_css_property("background-color")
        self.assertIn(bg, ["rgba(236, 253, 245, 1)", "rgb(236, 253, 245)"],
                      f"KC2 Assert 2 FAIL: Mau nen '{bg}' khong phai xanh la! (TC_PAY_003)")
        text = Select(pay_el2).first_selected_option.text
        self.assertIn("thanh to\u00e1n", text.lower(),
                      f"KC2 Assert 2 FAIL: Text '{text}' sai! (TC_PAY_003)")
        print(f"  [PASS] Assert 2: Mau = '{bg}', text = '{text}'. (TC_PAY_003)")

    # ----------------------------------------------------------
    # KICH BAN 3: Huy don hang + Kiem tra UI an nut
    # TC_ORDER_022, TC_ORDER_026, TC_SHIP_039
    # ----------------------------------------------------------
    def test_3_kich_ban_3_huy_don_hang_va_kiem_tra_UI(self):
        """[KC3] Huy don hang va kiem tra logic UI an nut"""
        driver = self.driver

        navigate_to_orders(driver)

        row = find_order_row_by_id(driver, ORDER_ID_SCENARIO_3)
        status_el = get_status_select_in_row(driver, row, ORDER_ID_SCENARIO_3)
        current = status_el.get_attribute("value")
        print(f"  [INFO] Trang thai hien tai order {ORDER_ID_SCENARIO_3}: {current}")

        human_select_by_value(status_el, "canceled")
        print("  [ACTION] Chon 'canceled'.")
        time.sleep(2)

        status_el2 = wait(driver).until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            f"select[aria-label='Tr\u1ea1ng th\u00e1i \u0111\u01a1n {ORDER_ID_SCENARIO_3}']"
        )))
        self.assertEqual(status_el2.get_attribute("value"), "canceled",
                         "KC3 Assert 1 FAIL: Badge khong phai 'canceled'! (TC_ORDER_022)")
        print("  [PASS] Assert 1: Badge = 'canceled'. (TC_ORDER_022)")

        row2 = find_order_row_by_id(driver, ORDER_ID_SCENARIO_3)
        btns = row2.find_elements(By.XPATH,
                                  ".//button[contains(text(),'Qu\u1ea3n l\u00fd giao v\u1eadn')]")
        self.assertEqual(len(btns), 0,
                         f"KC3 Assert 2 FAIL: Van co {len(btns)} nut tren row da huy! (TC_ORDER_026)")
        print("  [PASS] Assert 2: findElements().size()==0. Nut da bi an. (TC_ORDER_026, TC_SHIP_039)")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    print("=" * 60)
    print("  UC XU LY DON HANG - SELENIUM AUTO TEST")
    print("  1 Chrome | 3 Kich ban | Chay 1 lan roi dung")
    print("=" * 60)

    suite = unittest.TestLoader().loadTestsFromTestCase(AllScenarios)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"  Tong so test: {result.testsRun}")
    print(f"  PASS        : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  FAIL        : {len(result.failures)}")
    print(f"  ERROR       : {len(result.errors)}")
    print("=" * 60)

    sys.exit(0 if result.wasSuccessful() else 1)
