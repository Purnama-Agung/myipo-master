import hashlib
import math
import random
import json
import re
import time
import os
import subprocess as sub
import undetected_chromedriver as uc

from datetime import datetime
from selenium import webdriver

from src.html_parser import HtmlParser
from src.browser import Browser
from src.crawler import PATH_SAVE
from lib.logger import Logger

from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

class Myipo:
    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)
        self.url = "https://iponlineext.myipo.gov.my/SPHI/Extra/Default.aspx?sid=637957369978260196"
        self.ApdataTitle = 'div[id="MainContent_ctrlPT_tblCaseData"] .col-sm-2.label'
        self.ApdataValue = 'div[id="MainContent_ctrlPT_tblCaseData"] .col-sm-4.data'
        self.ContactTitle = 'div[id="MainContent_ctrlPT_tblCustomer"] .col-sm-2.label'
        self.ContactValue = 'div[id="MainContent_ctrlPT_tblCustomer"] .col-sm-10.data'
        self.PIdataTitle = 'div[id="MainContent_ctrlPT_upPatentInfo"] .col-sm-2.label'
        self.PIdataValue = 'div[id="MainContent_ctrlPT_upPatentInfo"] .col-sm-10.data'
        self.DocumentsTitle = 'div[id="MainContent_ctrlPT_tblDocuments"] .col-sm-2.label'
        self.DocumentsValue = 'div[id="MainContent_ctrlPT_tblDocuments"] .col-sm-10.data'
        self.parser = HtmlParser()
        self.browser = None
        self.display = None
        self.category = None
        self.dateStart = None
        self.dateEnd = None

    def create_path(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_proxy(self, choice=True):
        result = []
        try:
            if choice:
                proxy_type = ['proxy_cloud', 'proxy_cloud_1']
                br = Browser('http://192.168.29.129:5005/proxy?type={}'.format(random.choice(proxy_type)))
                html = br.get_html_request()

                proxies = json.loads(html)
                if proxies:
                    address = proxies['data']['ip']
                    port = proxies['data']['port']
                    temp = {'address': address, 'port': int(port)}
                    result.append(temp)
        except:
            raise
        return result

    def get_browser(self, isproxy=True):
        address = port = None
        if isproxy:
            item = self.get_proxy()
            address = item[0]['address']
            port = item[0]['port']
            self.logger.log('use proxy: {}:{}'.format(address, port))

        profile = FirefoxProfile()
        profile.set_preference('network.proxy.type', 1)
        profile.set_preference('network.proxy.http', address)
        profile.set_preference('network.proxy.http_port', int(port))
        profile.set_preference('network.proxy.ssl', address)
        profile.set_preference('network.proxy.ssl_port', int(port))
        profile.set_preference('network.proxy.socks', address)
        profile.set_preference('network.proxy.socks_port', int(port))
        profile.set_preference('network.proxy.ftp', address)
        profile.set_preference('network.proxy.ftp_port', int(port))

        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True
        browser = webdriver.Firefox(profile, capabilities=firefox_capabilities, log_path="/dev/null")
        return browser

    def get_browser_chrome(self, proxy=False):
        address = port = None
        if proxy:
            item = self.get_proxy()
            address = item[0]['address']
            port = item[0]['port']
            self.logger.log('use proxy: {}:{}'.format(address, port))

        chrome_options = uc.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--dns-prefetch-disable')

        # For ChromeDriver version 79.0.3945.16 or over
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        capabilities = dict(DesiredCapabilities.CHROME)
        if not "chromeOptions" in capabilities:
            capabilities['chromeOptions'] = {
                'args': [],
                'binary': "",
                'extensions': [],
                'prefs': {}
            }
        capabilities['proxy'] = {
            'httpProxy': '{}:{}'.format(address, port),
            'httpsProxy': '{}:{}'.format(address, port),
            "ftpProxy": '{}:{}'.format(address, port),
            "sslProxy": '{}:{}'.format(address, port),
            'noProxy': None,
            'proxyType': "MANUAL",
            'class': "org.openqa.selenium.Proxy",
            'autodetect': False
        }

        browser = uc.Chrome(chrome_options=chrome_options, desired_capabilities=capabilities)
        browser.execute_script('return navigator.webdriver')
        return browser

    def save_path_data(self, category, type, page_actualy, date_start, date_end):
        if date_start == date_end:
            path_date = '{}'.format(date_end)
        else:
            path_date = '{}-{}'.format(date_start, date_end)

        path_file = "{}/{}/page_{}".format(PATH_SAVE, path_date, page_actualy)
        if type == 'index':
            index_file_name = '{}_{}.html'.format(str(type), str(page_actualy))
            file_exists = os.path.isfile('{}/{}'.format(path_file, index_file_name))
            if not file_exists:
                index_path = self.create_path(path_file)
                with open("{}/{}".format(index_path, index_file_name), 'w+') as f:
                    self.logger.log('[{}] - new file saved {}'.format(category, index_file_name))
                    f.write(self.browser.page_source)
            else:
                self.logger.log('[{}] - file {} already exists !'.format(category, index_file_name))

    def get_index(self, category=None, date_start=None, date_stop=None, page_start=None, page_end=None):
        status = True
        while status:
            try:
                self.dateStart = datetime.strptime(date_start, '%Y%m%d').strftime('%d/%m/%Y')
                self.dateEnd = datetime.strptime(date_stop, '%Y%m%d').strftime('%d/%m/%Y')

                self.browser = self.get_browser_chrome()
                self.browser.get(self.url)

                # Wait content main
                WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main_content"]')))
                time.sleep(1)

                # Get Name Categories
                titleCategory = self.browser.find_elements_by_css_selector("div:nth-child({}) > div.col-sm-4 h3".format(category))[0].text
                self.category = re.sub('[\W]+', '', titleCategory).upper()

                # Click Categories
                self.logger.log('INDEX: CLICK CRITERIA [{}]'.format(self.category))
                WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.ID, 'MainContent_lnkPTSearch')))
                self.browser.find_element_by_id('MainContent_lnkPTSearch').click()
                time.sleep(random.uniform(1, 1.2))

                # Click Advanced Search
                WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.ID, 'MainContent_ctrlPTSearch_lnkAdvanceSearch')))
                self.logger.log('[{}] - CLICK ADVANCED SEARCH'.format(self.category))
                self.browser.find_element_by_id('MainContent_ctrlPTSearch_lnkAdvanceSearch').click()
                time.sleep(random.uniform(0.5, 1))

                # Filling Date Start
                WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="MainContent_ctrlPTSearch_txtFilingDateStart"]')))
                dateStart = self.browser.find_element_by_id('MainContent_ctrlPTSearch_txtFilingDateStart')
                self.browser.execute_script("arguments[0].scrollIntoView();", dateStart)
                dateStart.clear()
                dateStart.send_keys('{}'.format(str(self.dateStart)))
                time.sleep(random.uniform(1, 1.2))

                # Filling Date End
                dateEnd = self.browser.find_element_by_id('MainContent_ctrlPTSearch_txtFilingDateEnd')
                self.browser.execute_script("arguments[0].scrollIntoView();", dateEnd)
                dateEnd.clear()
                dateEnd.send_keys('{}'.format(str(self.dateEnd)))
                self.logger.log('[{}] - INSERT DATE FROM [{}] TO [{}]'.format(self.category, self.dateStart, self.dateEnd))
                time.sleep(random.uniform(1, 1.2))

                # Click search data
                search_button = self.browser.find_element_by_id('MainContent_ctrlPTSearch_lnkbtnSearch')
                self.browser.execute_script("arguments[0].scrollIntoView();", search_button)
                time.sleep(random.uniform(0.5, 1))
                self.logger.log('[{}] - CLICK SEARCH DATA'.format(self.category))
                search_button.click()

                # cek total pages
                try:
                    WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases')))
                    time.sleep(random.uniform(1, 2))
                    total_detail = self.browser.find_elements_by_id('MainContent_ctrlPTSearch_ctrlProcList_hdrNbItems')[0].text
                    total_pages = re.sub('(^[0-9]+).*', '\g<1>', total_detail.strip())
                    total_page = int(math.ceil(int(total_pages) / 50))
                except:
                    total_page = 1

                self.logger.log('[{}] - total pages is {}'.format(self.category, total_page))

                if not page_start:
                    pageStart = 1
                else:
                    pageStart = int(page_start)

                if not page_end:
                    pageEnd = int(total_page)
                else:
                    if int(page_end) >= int(total_page):
                        pageEnd = int(total_page)
                    else:
                        pageEnd = int(page_end)

                new_total_details = self.browser.find_elements_by_xpath(
                    '//*[@id="MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases"]/tbody/tr/td[2]/a')
                if int(len(new_total_details)) == 0:
                    try:
                        WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.tab-content.card-block')))
                    except:
                        pass
                    detail_check = self.browser.find_elements_by_css_selector('.tab-content.card-block')
                    if int(len(detail_check)) > 0:
                        time.sleep(random.uniform(0.8, 1))
                        self.browser.back()
                        detail_xpath = '//*[@id="MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases"]/tbody/tr[2]/td[2]/a'
                        WebDriverWait(self.browser, 20).until(EC.visibility_of_element_located((By.XPATH, detail_xpath)))
                        time.sleep(random.uniform(0.8, 1))
                        self.save_path_data(type='index', page_actualy=1, category=self.category, date_start=date_start, date_end=date_stop)

                        if date_start == date_stop:
                            path_date = '{}'.format(date_stop)
                        else:
                            path_date = '{}-{}'.format(date_start, date_stop)
                        path_file = "{}/{}/page_1".format(PATH_SAVE, path_date)
                        detail = self.browser.find_element_by_xpath(detail_xpath)
                        detail_title = re.sub(r"\W+", "_", detail.text.strip()).encode('utf-8')
                        detail_title_hash = "1_{}.html".format(hashlib.md5(detail_title).hexdigest())
                        detail_file_exists = os.path.isfile("{}/{}".format(path_file, detail_title_hash))
                        if not detail_file_exists:
                            self.browser.execute_script("arguments[0].scrollIntoView();", detail)
                            time.sleep(random.uniform(1, 1.5))
                            detail.click()
                            WebDriverWait(self.browser, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '.tab-content.card-block')))
                            time.sleep(random.uniform(0.8, 1))
                            with open("{}/{}".format(path_file, detail_title_hash), 'w+') as f:
                                f.write(self.browser.page_source)
                            self.logger.log('[{}] - save detail {}'.format(self.category, detail_title_hash))
                            time.sleep(random.uniform(0.8, 1))
                        else:
                            self.logger.log('[{}] - file {} already exists !'.format(self.category, detail_title_hash))
                    else:
                        self.logger.log('[{}] - no detail found in [{}] - [{}]'.format(self.category, self.dateStart, self.dateEnd))
                        time.sleep(random.uniform(0.8, 1))
                        self.save_path_data(type='index', page_actualy=1, category=self.category, date_start=date_start, date_end=date_stop)
                else:
                    for i_p in range(int(pageStart), int(pageEnd) + 1):
                        self.logger.log('[{}] - start from page {} - {}'.format(self.category, pageStart, pageEnd))
                        self.logger.log('[{}] - loop page {}'.format(self.category, i_p))
                        time.sleep(random.uniform(0.5, 0.8))
                        WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.ID, 'MainContent_ctrlPTSearch_upProcList')))

                        index_next = True
                        while index_next:
                            # cek page actualy
                            time.sleep(random.uniform(1.3, 2))
                            if int(pageEnd) == 1:
                                pg = '1'
                            else:
                                page_actual = self.browser.find_element_by_css_selector('#MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases > tbody > tr.gridview_pager > td > table > tbody > tr > td > span').text
                                pg = re.sub(r'[\W]+', '', page_actual).strip()

                            page_of_lists = self.browser.find_elements_by_css_selector('#MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases > tbody > tr.gridview_pager > td > table > tbody > tr > td')
                            self.logger.log("[{}] - page actualy {} page loop {}".format(self.category, pg, i_p))
                            if pg != str(i_p):
                                if int(pg) > int(i_p):
                                    self.logger.log("[{}] - before page {}".format(self.category, str(int(pg) + 1)))
                                    time.sleep(1)
                                    page_lists = [page_list.text for page_list in page_of_lists].index(str(pg))
                                    beforePage = int(page_lists) - 1
                                    self.browser.find_elements_by_css_selector('#MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases > tbody > tr.gridview_pager > td > table > tbody > tr > td:nth-child({})'.format(beforePage))[0].click()
                                    time.sleep(random.uniform(3, 4))
                                else:
                                    page_lists = [page_list.text for page_list in page_of_lists].index(str(pg))
                                    self.logger.log("[{}] - next page {}".format(self.category, str(int(pg) + 1)))
                                    nextPage = int(page_lists) + 2
                                    self.browser.find_elements_by_css_selector('#MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases > tbody > tr.gridview_pager > td > table > tbody > tr > td:nth-child({})'.format(nextPage))[0].click()
                                    WebDriverWait(self.browser, 20).until_not(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                      '.modal-backdrop.show')))
                                    time.sleep(random.uniform(1, 1.6))
                            else:
                                self.logger.log("[{}] - next page stop".format(self.category))
                                index_next = False

                        new_total_details = self.browser.find_elements_by_xpath('//*[@id="MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases"]/tbody/tr/td[2]/a')
                        self.logger.log("[{}] - total details {} in page {}".format(self.category, int(len(new_total_details)), pg))

                        path_date = '{}-{}'.format(date_start, date_stop)
                        if date_start == date_stop:
                            path_date = '{}'.format(date_start)

                        path_file = "{}/{}/page_{}".format(PATH_SAVE, path_date, pg)
                        out = "find {} -type f | wc -l".format(path_file)
                        total_file = sub.check_output(out, stderr=sub.STDOUT, shell=True, close_fds=True)
                        total_file = str(total_file.decode('utf-8')).strip()
                        if "No such file" in total_file:
                            total_file = re.sub(r'.*\n(.*)', '\g<1>', total_file).strip()

                        index_filename = 'index_{}.html'.format(pg)
                        file_exists = os.path.isfile("{}/{}".format(path_file, index_filename))
                        if not file_exists:
                            index_path = self.create_path(path_file)
                            with open("{}/{}".format(index_path, index_filename), 'w+') as f:
                                f.write(self.browser.page_source)
                            self.logger.log('[{}] - save file {}'.format(self.category, index_filename))
                            self.logger.log("[{}] - total file details {} in page {}".format(
                                self.category, str(total_file), pg))
                        else:
                            self.logger.log('[{}] - file exists {}'.format(self.category, index_filename))
                            self.logger.log("[{}] - total file details {} in page {}".format(
                                self.category, str(int(total_file) - 1), pg))

                        total_file_details = sub.check_output(out, stderr=sub.STDOUT, shell=True, close_fds=True)
                        total_file_details = str(total_file_details.decode('utf-8')).strip()

                        if int(int(total_file_details) - 1) != int(len(new_total_details)):
                            self.get_detail(path=path_file, category=self.category)
                        else:
                            self.logger.log('[{}] - successfully get all details from page {}'.format(self.category, pg))
                status = False
                self.logger.log("[{}] - successfully get category [{}] - [{}]".format(self.category, self.dateStart, self.dateEnd))
            except Exception as e:
                print(e)
                raise
            finally:
                self.browser.quit()
                self.logger.log('browser closed !')

    def get_detail(self, path, category):
        try:
            total_details = self.browser.find_elements_by_xpath(
                '//*[@id="MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases"]/tbody/tr/td[2]/a')
            for i in range(2, int(len(total_details)) + 2):
                detail_xpath = '//*[@id="MainContent_ctrlPTSearch_ctrlProcList_gvwIPCases"]/tbody/tr[{}]/td[2]/a'.format(i)
                detail = self.browser.find_element_by_xpath(detail_xpath)
                detail_title = re.sub("\W", "_", detail.text).encode('utf-8')
                detail_title_hash = "{}_{}.html".format(int(i) - 1, hashlib.md5(detail_title).hexdigest())

                detail_file_exists = os.path.isfile("{}/{}".format(path, detail_title_hash))
                if not detail_file_exists:
                    self.browser.execute_script("arguments[0].scrollIntoView();", detail)
                    time.sleep(random.uniform(1, 1.5))
                    detail.click()
                    WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.tab-content.card-block')))
                    time.sleep(random.uniform(0.8, 1))
                    with open("{}/{}".format(path, detail_title_hash), 'w+') as f:
                        f.write(self.browser.page_source)
                    self.logger.log('[{}] - save detail {}'.format(category, detail_title_hash))
                    time.sleep(random.uniform(0.8, 1))
                    self.browser.back()
                    WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, detail_xpath)))
                    time.sleep(random.uniform(0.8, 1))
                else:
                    self.logger.log('[{}] - exists file {}'.format(category, detail_title_hash))
            self.logger.log('[{}] - successfully get {} details page'.format(category, len(total_details)))
        except Exception as e:
            print(e)
            raise

    def open_file(self, path):
        import codecs
        html = codecs.open(path, 'r')
        html = html.read()
        return html

    def parse(self, html_path):
        try:
            result = []
            html = self.open_file(html_path)

            tmp = dict()
            self.logger.log('path detail parser {}'.format(html_path))

            # Application Data
            apdata_title = self.parser.bs4_parser(html, self.ApdataTitle)
            apdata_value = self.parser.bs4_parser(html, self.ApdataValue)
            headtitle_apdata = self.parser.pyq_parser(html,
                                                      'span[id="MainContent_ctrlPT_headerCaseData_lblheader"]').text().strip()
            title_apdata = re.sub('\W+', '_', headtitle_apdata).lower()
            for titles, values in zip(apdata_title, apdata_value):
                title = titles.text.strip().lower().replace(' ', '_')
                value = values.text.strip()
                if title == '' and value == '':
                    pass
                else:
                    key_apdata = '{}_{}'.format(title_apdata, title)
                    tmp[key_apdata] = value

            # Contacts
            Headtitle_cs = self.parser.pyq_parser(html,
                                                  'span[id="MainContent_ctrlPT_headerCustomer_lblheader"]').text().strip()
            title_cs = re.sub('\W+', '_', Headtitle_cs).lower()
            cs_len = self.parser.pyq_parser(html,
                                            'div[id="MainContent_ctrlPT_ctrlApplicant_UpdatePanel1"] .container-fluid').text().strip()
            if cs_len != '':
                cs_title = self.parser.bs4_parser(html, self.ContactTitle)
                cs_value = self.parser.bs4_parser(html, self.ContactValue)
                for cs_titles, cs_values in zip(cs_title[-2:], cs_value[-2:]):
                    CStitles = cs_titles.text.strip().lower().replace(' ', '_').replace('-', '_')
                    CSvalues = cs_values.text.strip().replace('\n', ' ')
                    key_cs = '{}_{}'.format(title_cs, CStitles)
                    tmp[key_cs] = CSvalues

                for cs_table_titles, cs_table_values in zip(cs_title[0:-2], cs_value[0:-2]):
                    CS_table_titles = cs_table_titles.text.strip().lower().replace(' ', '_').replace('-', '_')
                    CS_table_values = cs_table_values.select('table.table.table-hover.table-striped')
                    CS_data = []
                    for tables in CS_table_values:
                        tables_title = tables.findAll('tr')[0]
                        tables_value = tables.findAll('tr')[1:]
                        titles = tables_title.findAll('th')
                        for IPCvalue in tables_value:
                            CS_tables_record = {}
                            values = IPCvalue.findAll('td')
                            if len(values) == 1:
                                continue
                            else:
                                for title, value in zip(titles, values):
                                    title_ = title.text.strip().lower().replace(' ', '_')
                                    value_ = value.text.strip()
                                    if title_ == '' and value_ == '':
                                        pass
                                    else:
                                        CS_tables_record[title_] = value_

                            CS_data.append(CS_tables_record)
                        key_tables = '{}_{}'.format(title_cs, CS_table_titles)
                        tmp[key_tables] = CS_data

            # Patent Information
            Headtitle_pi = self.parser.pyq_parser(html,
                                                  'span[id="MainContent_ctrlPT_HeaderInfo_lblheader"]').text().strip()
            title_pi = re.sub('\W+', '_', Headtitle_pi).lower()
            pi_len = self.parser.bs4_parser(html, 'div[id="MainContent_ctrlPT_upPatentInfo"]  .container-fluid')
            if len(pi_len) > 0:
                pi_title = self.parser.bs4_parser(html, self.PIdataTitle)
                pi_value = self.parser.bs4_parser(html, self.PIdataValue)
                for pi_titles, pi_values in zip(pi_title, pi_value):
                    PItitle = pi_titles.text.strip().lower().replace(' ', '_').replace('-', '_')
                    PIvalue = pi_values.text.strip()
                    if PItitle == 'inventors':
                        investor_data = []
                        tables = self.parser.bs4_parser(html,
                                                        'div[id="MainContent_ctrlPT_divInventor"] table.table-hover.table-striped')
                        for table in tables:
                            INVtitles = table.findAll('tr')[0]
                            INVvalues = table.findAll('tr')
                            titles = INVtitles.findAll('th')
                            if len(INVvalues) != 13:
                                for INVvalue in INVvalues[1:-1]:
                                    values = INVvalue.findAll('td')
                                    INV_record = {}
                                    if len(values) == 1:
                                        continue
                                    else:
                                        for title, value in zip(titles, values):
                                            title_ = title.text.strip().lower().replace(' ', '_')
                                            value_ = value.text.strip()
                                            if title_ == '' and value_ == '':
                                                pass
                                            else:
                                                INV_record[title_] = value_
                                    investor_data.append(INV_record)
                            else:
                                for INVvalue in INVvalues[1:-2]:
                                    values = INVvalue.findAll('td')
                                    INV_record = {}
                                    if len(values) == 1:
                                        continue
                                    else:
                                        for title, value in zip(titles, values):
                                            title_ = title.text.strip().lower().replace(' ', '_')
                                            value_ = value.text.strip()
                                            if title_ == '' and value_ == '':
                                                pass
                                            else:
                                                INV_record[title_] = value_
                                    investor_data.append(INV_record)
                        key_investor = '{}_{}'.format(title_pi, PItitle)
                        tmp[key_investor] = investor_data

                    elif PItitle == 'international_patent_classification':
                        patent_class = []

                        tables = self.parser.bs4_parser(html,
                                                        'div[id="MainContent_ctrlPT_divIPC"] table.table-hover.table-striped')
                        for table in tables:
                            IPCtitles = table.findAll('tr')[0]
                            IPCvalues = table.findAll('tr')[1:]
                            titles = IPCtitles.findAll('th')
                            for IPCvalue in IPCvalues:
                                values = IPCvalue.findAll('td')
                                IPC_record = {}

                                for title, value in zip(titles, values):
                                    title_ = title.text.strip().lower().replace(' ', '_')
                                    value_ = value.text.strip()
                                    if title_ == '' and value_ == '':
                                        pass
                                    else:
                                        IPC_record[title_] = value_
                                patent_class.append(IPC_record)

                        key_patent_class = '{}_{}'.format(title_pi, PItitle)
                        tmp[key_patent_class] = patent_class
                    else:
                        if PItitle == '' and PIvalue == '':
                            pass
                        else:
                            key_docs = '{}_{}'.format(title_pi, PItitle)
                            tmp[key_docs] = PIvalue
            else:
                self.logger.log('No patent information record !')
                pass

            # Documents
            Headtitle_doc = self.parser.pyq_parser(html,
                                                   'span[id="MainContent_ctrlPT_HeaderDocs_lblheader"]').text().strip()
            title_doc = re.sub('\W+', '', Headtitle_doc).lower()
            doc_len = self.parser.bs4_parser(html, '.container-fluid')
            if len(doc_len) > 0:
                doc_title = self.parser.bs4_parser(html, self.DocumentsTitle)
                doc_value = self.parser.bs4_parser(html, self.DocumentsValue)
                for titles, values in zip(doc_title, doc_value):
                    title = titles.text.strip().lower().replace(' ', '_')
                    value = values.text.strip()
                    if title == '' and value == '':
                        pass
                    else:
                        key_docs = '{}_{}'.format(title_doc, title)
                        tmp[key_docs] = value
            else:
                self.logger.log('No documents record !')
                pass

            result.append(tmp)
        except:
            raise
        return json.dumps(result)
