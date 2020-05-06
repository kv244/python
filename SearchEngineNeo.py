from bs4 import *
import urllib.request
from urllib.parse import urljoin
import re


class Crawler:

    _scan_bucket = dict()

    def __init__(self, dbname=None, dbg=False):
        pass

    # self.con = sqlite.connect(path+dbname)
    # self.dbname = path + dbname
    # self.debug = dbg
    # print("Using database: ", self.dbname)

    def __del__(self):
        pass

    # self.con.close()

    def add_to_scan_bucket(self, url, title=None):
        print("Adding ", url)
        if self.is_in_scan_bucket(url) is False:
            self._scan_bucket.add(hash(url), (url, title))
        else:
            print(url, "already in")

    def is_in_scan_bucket(self, url):
        return hash(url) in self._scan_bucket.keys()

    def crawl(self, root_page="http://www.comisarul.ro", depth=2):

        level = 0
        self.add_to_scan_bucket(root_page, '')

        while level < depth:

            try:
                html_page = urllib.request.urlopen(root_page)
            except:
                print("Can't open page")

            page_in = BeautifulSoup(html_page.read(), 'html.parser')
            links_in = page_in('a')
            for link in links_in:
                # print(link)
                if 'href' in dict(link.attrs):
                    url = urljoin(root_page, link['href'])

                if 'title' in dict(link.attrs):
                    title = link['title']
                else:
                    title = ''

                self.add_to_scan_bucket(url, title)


c=Crawler()
c.crawl()
