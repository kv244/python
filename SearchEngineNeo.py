from bs4 import *
import urllib.request
from urllib.parse import urljoin
import urllib.error
import re


class Scanner:

    eliminate = ['#', '=', '?', '(', '@', 'facebook', 'twitter', 'jpg', 'tag', 'pdf']

    def __init__(self, origin: str):
        """origin is the starting URL"""
        self.origin = origin
        self.output = []

    def scan(self, crawler, max_links=50):
        """scans the origin page and populates the links in the output list"""
        try:
            html_page = urllib.request.urlopen(self.origin)
        except:
            print("Other error in scanner " + self.origin)
            return

        limit = 0
        try:
            page_in = BeautifulSoup(html_page.read(), 'html.parser')
            links_in = page_in('a')
            for link in links_in:
                if 'href' in dict(link.attrs):
                    url = urljoin(self.origin, link['href'])
                else:
                    continue

                skip = [x for x in list(map(url.find, Scanner.eliminate)) if x != -1]
                if skip:
                    continue

                if hash(url) in Crawler.scanned.keys():
                    continue
                else:
                    Crawler.scanned[hash(url)] = url
                    limit = limit + 1
                    self.output.append(url)

                    if limit > max_links:
                        break

        except:
            print("Error reading.... continue")

        #    if 'title' in dict(link.attrs):
        #        title = link['title']
        #    else:
        #        title = ''

    def __get__(self, instance, owner):
        return self.output


class Crawler:
    """Drives the scanner"""

    scanned = {}  # the dictionary holding the hash of scanned urls

    def __init__(self, origin: str, generations: int):
        """origin = starting URL
        generations = how many jumps from origin"""

        if generations <= 1:
            generations = 1
        self._current_bucket = []  # scanned by the current generation scan
        self._swap_bucket = []
        self._current_bucket.append(origin)
        self._origin = origin
        self._generations = generations
        self.response = []
        # Crawler.scanned[hash(origin)] = origin

    def __get__(self, instance, owner):
        return self._origin

    def _build_response(self, items_scanned, scanned_from: str, generation: int):
        for item in items_scanned:
            response_item = ("From: " + scanned_from, "Linked: " + item, "In: " + str(generation))
            self.response.append(response_item)

    def _scan(self, generation: int):
        itm = 0

        for item in self._current_bucket:
            itm += 1
            scanner = Scanner(item)
            scanner.scan(self)  # max links
            self._swap_bucket.extend(scanner.output)
            self._build_response(scanner.output, item, generation)

    def crawl(self):
        """ for items in current bucket while gen < max gen
        if item not in scanned already, scan item --> swap bucket list; add item to scanned
        for items2 in swap bucket
        add scan item, items2 to response
        inc gen
        current bucket = scan bucket
        scan bucket = empty
        """

        g = 0
        while g <= self._generations:
            print("\nGeneration ", g)
            self._scan(g)
            self._current_bucket = self._swap_bucket
            self._swap_bucket = []
            g += 1

    def check(self):
        self.response.sort(key = lambda x:x[2])
        for datum in self.response:
            print(datum[0] + " -(" + datum[2] + ")-> " + datum[1])


c = Crawler("https://www.catavencii.ro/", 2)
c.crawl()
c.check()
