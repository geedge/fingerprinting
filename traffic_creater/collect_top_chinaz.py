from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
# from selenium.webdriver.common.by import
from selenium.common.exceptions import TimeoutException
from time import sleep, time
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import os
import csv

# from threading import Lock

if __name__ == '__main__':
    lock = threading.Lock()
    save_dir = "./result"
    save_file = "./top_china.csv"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    f_writer = open(os.path.join(save_dir, save_file), "a", newline="")
    csv_writer = csv.writer(f_writer)


def crawl_chinaz(uri):
    # print(uri)
    options = ChromeOptions()
    driver = Chrome(executable_path="./driver/chromedriver.exe", options=options)
    driver.minimize_window()
    try:
        driver.get(uri)
        h3s = driver.find_elements_by_tag_name("h3")
        for h3 in h3s:
            content = h3.text
            name, domain = content.split(" ")
            # print(domain)
            lock.acquire()
            csv_writer.writerow([domain])
            lock.release()
    except TimeoutException:
        print("timeout quit!")
    finally:
        driver.quit()


def run():
    end_page_num = 1000
    seeds = []
    for i in range(100, end_page_num):
        if i == 0:
            index = ""
        else:
            index = "_" + str(i + 1)
        seed = f"https://top.chinaz.com/all/index{index}.html"
        seeds.append(seed)
    # crawl_chinaz(seeds[1])

    with ThreadPoolExecutor(max_workers=10) as thread_pool:
        for uri in seeds:
            # print(uri)
            thread_pool.submit(crawl_chinaz, uri)


if __name__ == '__main__':
    run()
