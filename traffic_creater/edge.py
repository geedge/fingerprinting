from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver import FirefoxProfile, FirefoxOptions, Firefox
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException
from time import sleep, time, strftime, localtime
from utils.util import get_domains_1500, get_ip_filter_from_uri
from urllib.parse import urlparse
from scapy.all import AsyncSniffer, wrpcap
import sys
import os


def create_traffic(doh_uri, web_domain, broswer) -> None:
    doh_traffic_savepath = "./doh_traffic"
    if not os.path.exists(doh_traffic_savepath):
        os.mkdir(doh_traffic_savepath)

    web_traffic_savepath = "./web_traffic"
    if not os.path.exists(web_traffic_savepath):
        os.mkdir(web_traffic_savepath)

    page_load_timeout = 30

    # ip_filter = get_ip_filter_from_uri(doh_uri)
    # print("ip filter is %s" % ip_filter)
    # doh_snf = AsyncSniffer(filter="host (%s) and port 443" % ip_filter)
    # web_snf = AsyncSniffer(filter="host not (%s) and port 443" % ip_filter)

    if broswer == "firefox":
        options = FirefoxOptions()

        profile = FirefoxProfile()
        profile.DEFAULT_PREFERENCES["frozen"]["network.trr.mode"] = 3
        profile.DEFAULT_PREFERENCES["frozen"]["network.trr.uri"] = doh_uri
        profile.accept_untrusted_certs = True

        driver = Firefox(firefox_profile=profile, options=options, executable_path="./driver/geckodriver.exe")
    elif broswer == "edge":
        edge_doh_button_xpath = "/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div[8]/div[5]/div[1]/div[2]/div/div/input"
        # edge_current_doh_provider_button_xpath = "/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div[8]/div[5]/div[2]/div[1]/input"
        edge_selfdef_doh_provider_button_xpath = "/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div[8]/div[5]/div[2]/div[2]/input"
        # edge_selfdef_doh_uri_xpath = "/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div[8]/div[5]/div[2]/div[2]/label/div/div[2]/div/div/div/input"
        edge_selfdef_doh_uri_xpath = "/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div[8]/div[5]/div[3]/div/div/input"
        edge_other_xpath = "/html/body/div[1]/div/div[1]/div/div/div[2]/div/div/div[9]/div[3]/div[2]/div/div/input"  # 用作保存doh配置

        options = EdgeOptions()
        options.page_load_strategy = "none"
        options.use_chromium = True
        options.add_argument('--hide-scrollbars')

        driver = Edge(executable_path="./driver/msedgedriver.exe", options=options)

        driver.get("edge://settings/privacy")
        doh_button = driver.find_element_by_xpath(edge_doh_button_xpath)
        if not doh_button.is_selected():
            doh_button.send_keys(Keys.SPACE)
        if not doh_button.is_selected():
            print("fail to start DoH!")
            exit(-1)
        driver.find_element_by_xpath(edge_selfdef_doh_provider_button_xpath).send_keys(Keys.SPACE)
        driver.find_element_by_xpath(edge_selfdef_doh_uri_xpath).send_keys(doh_uri)
        driver.find_element_by_xpath(edge_other_xpath).send_keys(Keys.SPACE)
        driver.find_element_by_xpath(edge_other_xpath).send_keys(Keys.SPACE)

        sleep(5)  # wait for doh connection
    else:
        return None

    driver.set_page_load_timeout(page_load_timeout)
    if not web_domain.startswith("https://"):
        web_domain = "https://%s" % web_domain

    # doh_traffic_savename = "%s/%s_%s_%s_%s.pcap" % (
    #     doh_traffic_savepath, urlparse(web_domain).netloc, urlparse(doh_uri).netloc, broswer,
    #     strftime("%Y-%m-%d-%H", localtime(time())))
    # web_traffic_savename = "%s/%s_%s_%s_%s.pcap" % (
    #     web_traffic_savepath, urlparse(web_domain).netloc, urlparse(doh_uri).netloc, broswer,
    #     strftime("%Y-%m-%d-%H", localtime(time())))
    try:
        # doh_snf.start()
        # web_snf.start()

        driver.get(web_domain)

        # wrpcap(doh_traffic_savename, doh_snf.stop())
        # wrpcap(web_traffic_savename, web_snf.stop())
        print("suc create traffic %s %s" % (web_domain, doh_uri))
    except TimeoutException as e:
        print("timeout quit!")
        # wrpcap(doh_traffic_savename, doh_snf.stop())
        # wrpcap(web_traffic_savename, web_snf.stop())
        print("suc create traffic %s %s" % (web_domain, doh_uri))
    except WebDriverException:
        print("WebDriverException", web_domain)
        # doh_snf.stop()
        # web_snf.stop()
    sleep(30)  # 等待流结束
    # if broswer == "firefox":
    #     sleep(30)  # 等待流结束
    driver.quit()


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        broswer = sys.argv[1]
    else:
        broswer = "edge"
    quad9_doh_uri = "https://dns.quad9.net/dns-query"
    google_doh_uri = "https://dns.google/dns-query"
    cloudflare_doh_uri = "https://mozilla.cloudflare-dns.com/dns-query"

    domains = get_domains_1500()
    for doh_uri in [cloudflare_doh_uri, quad9_doh_uri, google_doh_uri]:
        for domain in domains:
            create_traffic(doh_uri=doh_uri, web_domain=domain, broswer=broswer)
