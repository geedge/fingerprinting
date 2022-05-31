from selenium.webdriver import Edge
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
# from selenium.webdriver.common.by import
from selenium.common.exceptions import TimeoutException, WebDriverException
from time import sleep, time, strftime, localtime
import json
import csv
from concurrent.futures import ThreadPoolExecutor
from random import randint, shuffle
import threading
import platform

if __name__ == '__main__':
    lock = threading.Lock()
    if platform.platform().startswith("Windows"):
        driver_file = "./driver/msedgedriver.exe"
    else:
        driver_file = "./driver/msedgedriver"


def open_doh(driver: WebDriver, uri):
    doh_customer_button_xpath = "/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div[9]/div[2]/div/div[4]/div[2]/div[2]/input"
    doh_customer_text_xpath = "/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div[9]/div[2]/div/div[4]/div[3]/div/div/input"
    other_button_xpath = "/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div[10]/div[2]/div/div[2]/div[2]/div/div/input"
    driver.get("edge://settings/privacy")
    customer_button = driver.find_element_by_xpath(doh_customer_button_xpath)
    customer_button.send_keys(Keys.SPACE)
    customer_text = driver.find_element_by_xpath(doh_customer_text_xpath)
    customer_text.send_keys(uri)
    other_button = driver.find_element_by_xpath(other_button_xpath)
    other_button.send_keys(Keys.SPACE)
    sleep(3)  # 等待DoH服务建立连接


def visited_website_with_doh(website, doh_uri):
    driver = Edge(executable_path=driver_file)
    open_doh(driver, doh_uri)
    try:
        driver.get(website)
    except TimeoutException:
        print("timeout quit!", website)
    except WebDriverException:
        print("WebDriverException", website)
    finally:
        driver.quit()


def visited_websites_with_doh(websites, doh_uri):
    print(websites)
    driver = Edge(executable_path=driver_file)
    driver.set_page_load_timeout(10)
    open_doh(driver, doh_uri)
    for website in websites:
        try:
            driver.get(website)
        except TimeoutException:
            print("timeout quit!", website)
        except WebDriverException:
            print("WebDriverException", website)
    driver.quit()


def run_with_thread_pool(websites, thread_num, doh_uri):
    website_nums = len(websites)
    with ThreadPoolExecutor(max_workers=thread_num) as thread_pool:
        count = 0
        while count < website_nums:
            # scan_num = randint(4, 6)
            scan_num = 1
            low_bound = count
            upper_bound = min(count + scan_num, len(websites))
            count += scan_num

            visit_websites = websites[low_bound: upper_bound]
            thread_pool.submit(visited_websites_with_doh, visit_websites, doh_uri)


def run():
    website_nums = 1000
    thread_num = 10
    ali_doh_uri = "https://223.5.5.5/dns-query"
    repeat_num = 20

    websites = []
    with open("./result/top_china.csv") as fp:
        csv_reader = csv.reader(fp)
        for row in csv_reader:
            domain = row[0]
            uri = f"https://{domain}"
            websites.append(uri)
            if len(websites) >= website_nums:
                break

    for _ in range(repeat_num):  # 重复多次
        shuffle(websites)  # 每次网站访问顺序不同
        run_with_thread_pool(websites, thread_num, ali_doh_uri)


if __name__ == '__main__':
    print("start", strftime('%y-%m-%d:%H:%M:%S', localtime(time())))
    run()
    print("end", strftime('%y-%m-%d:%H:%M:%S', localtime(time())))
    # websites = []
    # visited_websites_with_doh(["https://qq.com/"], "https://223.5.5.5/dns-query")
