from bs4 import *
import urllib.request
from urllib.parse import urljoin
import urllib.error
import re


class Scanner:

    eliminate = ['#', '=', '?', '(', '@', 'facebook']

    def __init__(self, origin: str):
        self.origin = origin
        self.output = []

    def scan(self, crawler, max_links=50):
        """scans the origin page and populates the links in the output list"""
        try:
            html_page = urllib.request.urlopen(self.origin)
        except:
            print("Other error in scanner " + self.origin)
            return

        # print("\tIn scanner - scanning " + self.origin + " for links.\n")

        limit = 0
        try:
            page_in = BeautifulSoup(html_page.read(), 'html.parser')
            links_in = page_in('a')
            print("\tScanner found: " + str(len(links_in)) + " links.")
            for link in links_in:
                if 'href' in dict(link.attrs):
                    url = urljoin(self.origin, link['href'])
                else:
                    continue

            # print("\t...", url)
            # skip = map(url.find, Scanner.eliminate)
            # print(skip)

                if url.find("#") != -1:
                    continue
                if url.find("=") != -1:
                    continue
                if url.find("?") != -1:
                    continue
                if url.find("(") != -1:
                    continue
                if url.find("@") != -1:
                    continue
                if url.find("facebook") != -1:
                    continue
                if url.find("twitter") != -1:
                    continue
                if url.find("jpg") != -1:
                    continue

                if hash(url) in Crawler.scanned.keys():
                    # print("\t\tAlready scanned")
                    continue
                else:
                    Crawler.scanned[hash(url)] = url
                    print("\t\tAdding to scanned list " + str(url) + " Sizeof scanned can: " + str(len(Crawler.scanned)))
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

    scanned = {}

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
        self.response = set()
        Crawler.scanned[hash(origin)] = origin

    def __get__(self, instance, owner):
        return self._origin

    def _build_response(self, scanned_from: str, generation: int):
        for item in self._swap_bucket:
            response_item = ("From: " + scanned_from, "Linked: " + item, "In: " + str(generation))
            self.response.add(response_item)

    def _scan(self, generation: int):
        itm = 0
        print("Bucket size ", len(self._current_bucket))

        for item in self._current_bucket:
            print("\n\t" + str(generation) + " reading item " + str(itm) + " from bucket: " + item)

            itm += 1
            scanner = Scanner(item)
            scanner.scan(self)
            self._swap_bucket.extend(scanner.output)
            self._build_response(item, generation)

    def crawl(self):

        # for items in current bucket while gen < max gen
        # if item not in scanned already, scan item --> swap bucket list; add item to scanned
        # for items2 in swap bucket
        # add scan item, items2 to response
        # inc gen
        # current bucket = scan bucket
        # scan bucket = empty

        g = 0
        while g <= self._generations:
            print("\nGeneration ", g)
            self._scan(g)

            self._current_bucket = self._swap_bucket
            self._swap_bucket = []
            g += 1

    def check(self):
        for datum in self.response:
            for data in datum:
                print("\t", data)
            print("\n")


c = Crawler("https://www.catavencii.ro/", 2)
c.crawl()
c.check()
