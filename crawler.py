import os
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import csv
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# define CONST VARIABLE
HOUSE_NAME_CLASS = "AdDecriptionVeh_adTitle__vEuKD"
HOUSE_PRICE_CLASS = "AdDecriptionVeh_price__u_N83"
HOUSE_GENERAL_INFO_CLASS = "DetailView_adviewPtyItem__V_sof"
HOUSE_LINK_DETAIL_CLASS = ".AdItem_adItem__gDDQT"
DEFAULT_HOME_URL = "https://www.nhatot.com/mua-ban-nha-dat"
# LOCATIONS = {"HO CHI MINH": "tp-ho-chi-minh", "HA NOI": "ha-noi", "DA NANG": "da-nang"}
LOCATIONS = {"da-nang": 50, "ha-noi": 100, "tp-ho-chi-minh": 150}
# LOCATIONS = {"tp-ho-chi-minh": 450}


# define option
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument(
    "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
)

# define browser

columns = [
    "Diện tích đất:",
    "Số phòng ngủ:",
    "Số phòng vệ sinh:",
    "Giấy tờ pháp lý:",
    "Loại hình nhà ở:",
    "Chiều ngang:",
    "Diện tích sử dụng:",
    "Giá/m2:",
    "Hướng cửa chính:",
    "Tổng số tầng:",
    "Đặc điểm nhà/đất:",
    "Tình trạng nội thất:",
    "Chiều dài:",
    "Location",
    "Name",
    "URL",
    "District",
    "Price",
]


def setter(house, label, data):
    if label in columns:
        house[label] = data


cnt = 0

for location, page_max in LOCATIONS.items():
    page_count = 0
    page = -1
    while page < page_max:
        page += 1
        if page % 50 == 0:
            csv_file = open(
                "./data" + f"/page_nha_dat_{location}_{page//50}.csv",
                "w",
                encoding="utf8",
            )
            writer = csv.DictWriter(csv_file, columns)
            writer.writeheader()
        # Mở page
        driver = webdriver.Chrome(options=options)
        driver.get(
            f"https://www.nhatot.com/mua-ban-can-ho-chung-cu-{location}?page={page}"
        )
        # Chờ lấy được link item
        time.sleep(2)
        link_items = driver.find_elements(By.CSS_SELECTOR, HOUSE_LINK_DETAIL_CLASS)
        house_urls = [str(link_item.get_attribute("href")) for link_item in link_items]
        driver.quit()

        for url in house_urls[:2]:
            crawl_driver = webdriver.Chrome(options=options)
            crawl_driver.get(url)
            try:
                general_info = crawl_driver.find_elements(
                    By.CLASS_NAME, HOUSE_GENERAL_INFO_CLASS
                )[1]
                house = {}
                house["Name"] = crawl_driver.find_elements(
                    By.CLASS_NAME, HOUSE_NAME_CLASS
                )[0].text
                house["District"] = crawl_driver.find_elements(By.CLASS_NAME, "fz13")[
                    0
                ].get_attribute("textContent")
                house["Location"] = location
                try:
                    btn = WebDriverWait(general_info, 2).until(
                        EC.element_to_be_clickable((By.TAG_NAME, "button"))
                    )
                    btn.click()
                except:
                    pass
                finally:
                    pass

                try:
                    details = WebDriverWait(general_info, 2).until(
                        EC.visibility_of_all_elements_located(
                            (By.CLASS_NAME, "AdParam_adMediaParam__3epxo")
                        )
                    )
                    if len(details) > 0:
                        for detail in details:
                            _, label, data = detail.find_elements(By.TAG_NAME, "span")
                            setter(house, label.text, data.text)
                except:
                    pass
                finally:
                    writer.writerow(house)
            except:
                pass
            finally:
                crawl_driver.quit()
        if page % 50 == 49:
            csv_file.close()
