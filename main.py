import asyncio
from datetime import datetime
from typing import Final
import pandas as pd
import tracemalloc
import seleniumwire.undetected_chromedriver.v2 as uc
import time

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tools.iproxy import get_change_ip_url
from tools.logger import init_logger

MAIN_URL: Final = "multicity.23met.ru"
ROUTERS: Final = [
    "price",
    "price_nerzh",
    "price_aluminium",
    "price_bronza",
    "price_volfram",
    "price_latun",
    "price_magniy",
    "price_med",
    "price_nikel",
    "price_nihrom",
    "price_olovo",
    "price_svinec",
    "price_titan",
    "price_cink",
    "price_cirkoniy",
]

tracemalloc.start()
logger = init_logger("main")
result = pd.DataFrame()

try:
    logger.info("Подготовка...")
    proxyString = "kudrinalexanderp264027" + ":" + "7875370" + "@" + "x155.fxdx.in" + ":" + "15414"

    wire_options = {
        'proxy': {
            'http': 'http://' + proxyString,
            'https': 'https://' + proxyString,
            'no_proxy': 'localhost,127.0.0.1'
        }
    }

    loop = asyncio.get_event_loop()
    change_ip_url = loop.run_until_complete(get_change_ip_url("a336"))
    loop.close()

    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    options.page_load_strategy = 'eager'

    # driver = uc.Chrome(version_main=112, seleniumwire_options=options)
    driver = uc.Chrome(version_main=112, options=options, seleniumwire_options=wire_options)
    # driver.implicitly_wait(10)

    logger.info("Начинаю парсинг...")
    for route in ROUTERS:
        try:
            driver.get(f"https://{MAIN_URL}/{route}")

            if driver.title == "Слишком много запросов":
                logger.warning("Обход блокировки. Смена IP...")
                driver.get(change_ip_url)
                time.sleep(30)
                driver.get(f"https://{MAIN_URL}/{route}")

            logger.info(f"Раздел: {driver.title.split('—')[0]}")

            driver.find_element(By.ID, "regionchooser-0").click()
            driver.find_element(By.CLASS_NAME, "citychooser-save-btn").click()
            time.sleep(5)

            driver.maximize_window()

            left_navbar = driver.find_element(By.ID, "left-container").find_element(By.TAG_NAME, "ul")
            left_tabs = left_navbar.find_elements(By.TAG_NAME, "li")
            for left_tab in left_tabs:
                try:
                    left_tab = left_tab.find_element(By.TAG_NAME, "span")
                    left_tab.click()
                    continue
                except:
                    pass
                left_tab = left_tab.find_element(By.TAG_NAME, "a")
                sub_route = left_tab.get_attribute("href").split("/")[4]
                left_tab.click()
                try:
                    center_navbar = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "center-container"))
                    )

                    time.sleep(5)
                    center_tabs = center_navbar.\
                        find_element(By.CSS_SELECTOR, f'div[data-naimenovanie="{sub_route}"]').\
                        find_elements(By.TAG_NAME, "a")

                    merged_df = pd.DataFrame()
                    for center_tab in center_tabs:
                        try:
                            sub_catalog = center_tab.get_attribute('href')
                            driver.switch_to.new_window()
                            driver.get(sub_catalog)

                            if driver.title == "Слишком много запросов":
                                logger.warning("Обход блокировки. Смена IP...")
                                driver.get(change_ip_url)
                                time.sleep(30)
                                driver.get(sub_catalog)

                            logger.info(f"Подраздел: {driver.title.split('—')[0]}")

                            table_prices = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.ID, "table-price"))
                            )

                            soup = BeautifulSoup(table_prices.get_attribute('outerHTML'), 'html.parser')
                            table = soup.find('table')
                            df = pd.read_html(str(table))[0]
                            merged_df = pd.concat([merged_df, df], ignore_index=True)

                        except Exception as e:
                            logger.error(f"Не удалось получить данные со страницы: {driver.current_url}")
                            logger.debug(e)

                        finally:
                            if len(driver.window_handles) > 1:
                                driver.close()

                            driver.switch_to.window(driver.window_handles[0])

                    result = pd.concat([result, merged_df], ignore_index=True)

                except TimeoutException:
                    logger.warning(f"Превышено время ожидания. Пропуск...")
                    continue
        except Exception as e:
            logger.debug(e)
            continue

except Exception as e:
    logger.critical("Критическая ошибка. Сохранение полученных данных...")
    logger.debug(e)
finally:
    driver.close()
    driver.quit()
    logger.warning("Парсер завершил работу.")

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    result.to_csv(f'data/{formatted_datetime}_source.csv', index=False)
    logger.info("Сохранил данные в исходном формате. Начинаю сортировку по городам...")

    dfs_by_city = {}
    result['Город'] = result['Поставщик'].str.split(" \(").str[0].str.split().str[-1]

    for city in result['Город'].unique():
        filtered_df = result[result['Город'] == city]
        filtered_df = filtered_df.drop('Город', axis=1)
        dfs_by_city[city] = filtered_df

    with pd.ExcelWriter(f'data/{formatted_datetime}_sort.xlsx') as writer:
        for city, city_df in dfs_by_city.items():
            city_df.to_excel(writer, sheet_name=city, index=False)

    logger.info(f"Данные отсортированы и записаны в папку data. Название файла: {formatted_datetime}_sort.xlsx")
