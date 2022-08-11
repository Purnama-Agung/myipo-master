import urllib3
import cloudscraper
import requests

from lib.logger import Logger

class Browser:
    def __init__(self, url):
        self.url = url
        self.logger = Logger(name=self.__class__.__name__)
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7,ms;q=0.6',
            'accept-charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'accept-encoding': 'none',
            'connection': 'keep-alive',
            'cache-control': 'max-age=0',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }

    def get_html(self):
        html = None
        try:
            urllib3.disable_warnings()
            req = urllib3.PoolManager()
            response = req.request(method='GET', url=self.url, headers=self.headers)
            if response:
                html = response.data
        except:
            raise
        return html

    def get_html_cloudscraper(self, method='GET', **kwargs):
        html = None
        try:
            try:
                kwargs.update(dict(url=self.url, timeout=60))
                if not kwargs.get('headers'):
                    kwargs.update(headers=self.headers)

                if method.lower() == "post":
                    response = cloudscraper.create_scraper(allow_brotli=False).post(**kwargs)
                else:
                    response = cloudscraper.create_scraper(allow_brotli=False).get(**kwargs)
                response.raise_for_status()
                if response.status_code == int(200):
                    html = response.text
            except requests.exceptions.RequestException as e:
                self.logger.log(e, level='error')
                raise
        except:
            raise
        return html

    def get_html_request(self, method='GET', **kwargs):
        html = None
        try:
            try:
                kwargs.update(dict(url=self.url, timeout=60))
                if not kwargs.get('headers'):
                    kwargs.update(headers=self.headers)

                if method.lower() == "post":
                    response = requests.post(**kwargs)
                else:
                    response = requests.get(**kwargs)
                response.raise_for_status()
                if response.status_code == int(200):
                    html = response.text
            except requests.exceptions.RequestException as e:
                self.logger.log(e, level='error')
                raise
        except:
            raise
        return html
