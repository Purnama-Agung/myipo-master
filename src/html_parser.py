from bs4 import BeautifulSoup
from pyquery import PyQuery as pq


class HtmlParser:
    def __init__(self):
        pass

    def bs4_parser(self, html, selector):
        try:
            html = BeautifulSoup(html, 'lxml')
            result = html.select(selector)
        except:
            raise
        return result

    def pyq_parser(self, html, selector):
        try:
            html = pq(html)
            result = html(selector)
        except:
            raise
        return result
