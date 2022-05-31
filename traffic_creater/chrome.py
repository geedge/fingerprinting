from selenium.webdriver import Chrome, ChromeOptions
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
        driver_file = "./driver/chromedriver.exe"
    else:
        driver_file = "./driver/chromedriver"
doh_uri_list = [
    "https://doh.pub/dns-query",
    "https://dns.alidns/dns-query",
    "https://dns.doh.360.cn/dns-query",
    "https://public.dns.iij.jp/dns-query",
    "https://dns.quad9.net/dns-query",
    "https://family.canadianshield.cira.ca/dns-query",
    "https://dns.twnic.tw/dns-query",
    "https://dns.aa.net.uk/dns-query",
    "https://dns.nextdns.io/dns-query",
    "https://dnspriv.apnic.cn/dns-query",
]


def open_doh(driver: WebDriver, uri):
    driver.set_page_load_timeout(20)

    driver.get("chrome://settings/security")
    # driver.minimize_window()
    # print(driver.page_source)

    customer_button = driver.execute_script(
        'return '
        'document.querySelector("settings-ui")'
        '.shadowRoot.querySelector("settings-main")'
        '.shadowRoot.querySelector("settings-basic-page")'
        '.shadowRoot.querySelector("settings-privacy-page")'
        '.shadowRoot.querySelector("settings-security-page")'
        '.shadowRoot.querySelector("settings-secure-dns")'
        '.shadowRoot.querySelector("#secureResolverSelectRadioButton")'
    )
    customer_button.send_keys(Keys.SPACE)

    customer_address_bar = driver.execute_script(
        'return '
        'document.querySelector("settings-ui")'
        '.shadowRoot.querySelector("settings-main")'
        '.shadowRoot.querySelector("settings-basic-page")'
        '.shadowRoot.querySelector("settings-privacy-page")'
        '.shadowRoot.querySelector("settings-security-page")'
        '.shadowRoot.querySelector("settings-secure-dns")'
        '.shadowRoot.querySelector("secure-dns-input")'
    )
    # print(type(customer_address_bar), customer_address_bar)
    customer_address_bar.send_keys(uri)

    other = driver.execute_script(
        'return '
        'document.querySelector("settings-ui")'
        '.shadowRoot.querySelector("settings-main")'
        '.shadowRoot.querySelector("settings-basic-page")'
        '.shadowRoot.querySelector("settings-privacy-page")'
        '.shadowRoot.querySelector("settings-security-page")'
        '.shadowRoot.querySelector("settings-collapse-radio-button")'
        '.shadowRoot.querySelector("cr-expand-button")'
    )
    # print(type(other), other)
    other.send_keys(Keys.SPACE)
    sleep(3)  # 等待DoH服务建立连接


def visited_website_with_doh(website, doh_uri):
    options = ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--user-data-dir=' + p)
    # options.add_argument("--user-data-dir=C:\\Users\\JiaTing\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1")
    driver = Chrome(executable_path=driver_file, options=options)
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
    # print(websites)
    options = ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--user-data-dir=' + p)
    # options.add_argument("--user-data-dir=C:\\Users\\JiaTing\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1")
    driver = Chrome(executable_path=driver_file, options=options)
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
            scan_num = randint(4, 6)
            low_bound = count
            upper_bound = min(count + scan_num, len(websites))
            count += scan_num

            visit_websites = websites[low_bound: upper_bound]
            thread_pool.submit(visited_websites_with_doh, visit_websites, doh_uri)


def run_with_thread_pool_with_random_doh(websites, thread_num):
    website_nums = len(websites)
    with ThreadPoolExecutor(max_workers=thread_num) as thread_pool:
        count = 0
        index = 0
        while count < website_nums:
            scan_num = randint(4, 6)
            low_bound = count
            upper_bound = min(count + scan_num, len(websites))
            count += scan_num
            visit_websites = websites[low_bound: upper_bound]
            doh_uri = doh_uri_list[index % len(doh_uri_list)]
            index += 1
            thread_pool.submit(visited_websites_with_doh, visit_websites, doh_uri)


def run():
    website_nums = 20000
    thread_num = 10
    ali_doh_uri = "https://doh.pub/dns-query"
    repeat_num = 1

    low_bound = 15000
    up_bound = 20000
    if up_bound - low_bound > website_nums:
        print("error websites num!")
        return

    websites = []
    with open("./result/top_china.csv") as fp:
        csv_reader = csv.reader(fp)
        for row in csv_reader:
            domain = row[0]
            uri = f"https://{domain}"
            websites.append(uri)
            if len(websites) >= website_nums:
                break
    websites = websites[low_bound:up_bound]
    for i in range(repeat_num):  # 重复多次
        shuffle(websites)  # 每次网站访问顺序不同
        run_with_thread_pool_with_random_doh(websites, thread_num)


if __name__ == '__main__':
    print("start", strftime('%y-%m-%d:%H:%M:%S', localtime(time())))
    run()
    print("end", strftime('%y-%m-%d:%H:%M:%S', localtime(time())))
    # websites = []
    # visited_website_with_doh("https://baidu.com/", "https://dnspriv.apnic.cn/dns-query")
