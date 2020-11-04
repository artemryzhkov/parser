#!/usr/bin/python
import pandas as pd
from crontab import CronTab
from selenium import webdriver
import json
from selenium.webdriver.common.keys import Keys
import time
import csv
import collections
import random
import sqlite3
from datetime import datetime
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


options = Options()
options.headless = True
driver = webdriver.Chrome(executable_path=r'/Users/data/Downloads/chromedriver')


def save_address():
    pass


def open_page(url):
    driver.get(url)
    save_address()


def get_elements(selector, **kwargs):
    parent = kwargs.get('parent', None)
    if parent is not None:
        return parent.find_elements_by_css_selector(selector)

    return driver.find_elements_by_css_selector(selector)


def get_product_item_name(item):
    name = get_elements('.DesktopProductItem_name', parent=item)
    return name[0].text


def get_price_of_product(item):
    try:
        price = get_elements('.DesktopProductItem_resultPrice', parent=item)
        price_str = price[0].text
        price_list = [int(s) for s in price_str.split() if s.isdigit()]
        for i in range(len(price_list)):
            return price_list[i]
    except:
        pass


def get_text_count(item):
    txt = get_elements('.DesktopProductItemCounter_value', parent=item)
    txt_str =  txt[0].text
    txt_list = [int(s) for s in txt_str.split() if s.isdigit()]
    for i in range(len(txt_list)):
        return txt_list[i]


def is_avialabel(item):
    try:
        avialabel = get_elements('.DesktopProductItem_notAvailable', parent=item)
        return avialabel
    except NoSuchElementException:
        pass


def get_product_item_add_button(item):
    button = get_elements('.DesktopProductItem_addButton', parent=item)
    if (len(button) == 0):
        pass
    else:
        return button[0]


def get_product_item_buttons(item):
    buttons = get_elements('.DesktopProductItemCounter_control', parent=item)
    return buttons


open_page('https://eda.yandex/restaurant/produkty_chamovniky?category=popular_60287&scope=global')
links = get_elements('a.DesktopGrocerySidebar_content')
urls = list(map(lambda link: link.get_attribute('href'), links))
print(urls)
results = []
names = []
i = 0
today = datetime.today().strftime('%d-%m-%Y %H:%M')
for url in urls:
    print(url)
    open_page(url)
    product_items = get_elements('li.DesktopSubcategory_item')
    for product in product_items:
        name = get_product_item_name(product)
        price = get_price_of_product(product)
        if isinstance(price, type(None)):
            results.append((i, today, name, 0, 0))
            i += 1
            continue
        avialabel = is_avialabel(product)
        if name not in names:
            if isinstance(avialabel, type(None)):
                results.append((i, today, name, 0, 0))
                i += 1
                continue
            add_button = get_product_item_add_button(product)
            try:
                if isinstance(add_button, type(None)):
                    results.append((i, today, name, 0, 0))
                    i += 1
                    continue
                else:
                    time.sleep(1)

                    add_button.click()
                try:
                    search_geo = driver.find_element_by_css_selector(
                        '.AppAddressInput_addressInput.AppAddressInput_modalStyle')
                    search_geo.send_keys('фрунзенская набережная, 20')
                    search_geo.send_keys(u'\ue007')
                    time.sleep(5)
                    search_geo_ok = driver.find_element_by_class_name('DesktopLocationModal_ok')
                    search_geo_ok.click()
                    time.sleep(2)
                    minus_button, plus_button = get_product_item_buttons(product)
                    while plus_button.is_enabled():
                        time.sleep(3)
                        plus_button.click()
                    txt = get_text_count(product)
                    results.append((i, today, name, txt, price))
                    i += 1
                except NoSuchElementException:
                    try:
                        minus_button, plus_button = get_product_item_buttons(product)
                        while plus_button.is_enabled():
                            time.sleep(0.05)
                            plus_button.click()
                        txt = get_text_count(product)
                        results.append((i, today, name, txt, price))
                        i += 1
                        names.append(name)
                    except ValueError:
                        print('VALUE ERROR: ', name)
                        continue
            except ElementClickInterceptedException or IndexError or AttributeError:
                print('ElementClickInterceptedException or IndexError or AttributeError ', name)
                continue


for result in results:
    print('Id: ', result[0], 'Date: ', result[1], 'Name: ', result[2], 'Count: ', result[3], 'Price: ', result[4])
    print('Id: ', type(result[0]), 'Date: ', type(result[1]), 'Name: ', type(result[2]), 'Count: ', type(result[3]), 'Price: ', type(result[4]))


driver.close()

conn = sqlite3.connect('ya_l.db')
cursor = conn.cursor()
for res in results:
    cursor.executemany('INSERT OR IGNORE INTO data values(?,?,?,?,? )', (res,))
    conn.commit()
conn.close()
