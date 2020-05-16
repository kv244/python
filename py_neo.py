"""This is a web crawler
Which stores data in Neo4J"""

# TODO read python book, data structures
# TODO improve code
# TODO then publish

import urllib.error
import urllib.request
from urllib.parse import urljoin

from bs4 import *
from neo4j import GraphDatabase


# TODO: 2) remove spurious stuff
# TODO: 1) edit creation queries to use tx


class Scanner:
    """Performs the actual web crawl"""

    eliminate: [str] = ['#', '=', '?', '(', '@', 'facebook', 'twitter', 'jpg', 'tag', 'pdf', 'png', 'youtu', 'feed',
                        'tel', 'microsoft', 'mozilla', 'google', 'pinterest', 'instagram', 'wikipedia', 'gravatar',
                        'imgur']
    """List of strings to be skipped from scanning"""

    @staticmethod
    def make_exception(ex: Exception):
        """Helper method to return a string from the exception"""

        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message

    def __init__(self, origin: str):
        """origin is the starting URL"""

        self.origin = origin
        self.output = []

    def scan(self, crawler, max_links=30):
        """scans the origin page and populates the links in the output list"""

        limit = 0
        try:
            html_page = urllib.request.urlopen(self.origin)
            page_in = BeautifulSoup(html_page.read(), 'html.parser')
            links_in = page_in('a')
            for link in links_in:
                if 'href' in dict(link.attrs):
                    url = urljoin(self.origin, link['href'])
                else:
                    continue

                if 'title' in dict(link.attrs):
                    title = link['title']
                else:
                    title = ''

                skip = [unwanted_link for unwanted_link in list(map(url.find, Scanner.eliminate))
                        if unwanted_link != -1]
                if skip:
                    continue

                if hash(url) in Crawler.scanned.keys():
                    continue
                else:
                    Crawler.scanned[hash(url)] = url  # TODO 3) add title here
                    limit = limit + 1
                    self.output.append(url)

                    if limit > max_links:
                        break

        except Exception as ex:
            print(Scanner.make_exception(ex))

    def __get__(self, instance, owner):
        return self.output


class Crawler:
    """Drives the scanner"""

    scanned = {}  # the dictionary holding the hash of scanned urls

    def __init__(self, origin: str, generations: int, db_url: str = "bolt://localhost:7687",
                 db_login: str = "gigifecali", db_pwd: str = "fecali"):
        """origin = starting URL
        generations = how many jumps from origin"""

        self._current_bucket = []  # scanned by the current generation scan
        self._swap_bucket = []
        self._current_bucket.append(origin)
        self._generations = generations
        self.storage = GraphStorage(db_url, db_login, db_pwd)

    @staticmethod
    def make_node(url_create: str, title: str = "") -> str:
        """Helper method to build a node creation command in Cypher"""
        p_var = "n"
        p_tag = "URL"
        p_prop = {"URL": url_create, "title": title}
        qry_make_node = GraphStorage.make_obj(p_var, p_tag, p_prop)
        return qry_make_node

    @staticmethod
    def make_rel(url_to: str, url_from: str) -> str:
        qry_make_rel = GraphStorage.make_rel("URL", "URL", url_from, "URL", "URL", url_to, "LINKS_TO")
        return qry_make_rel

    def _build_response(self, items_scanned, scanned_from: str, generation: int):
        """builds the response data structure for the crawl
        items_scanned is the collection of URLs scanned starting with scanned_from (string)
        generation is the number away from the origin"""

        for item in items_scanned:
            query_node = (Crawler.make_node(item, "NOTITLE_YET"))
            query_rel = (Crawler.make_rel(item, scanned_from))
            self.storage.run_command(query_node)
            self.storage.run_command(query_rel)

    def _scan(self, generation: int):
        """Crawls the URLs in the current bucket
        which results in a new list of links for each existing URL
        all of which are consolidated. It also builds the response
        for the source URL and the links generated for it in the current
        generation."""

        for item in self._current_bucket:
            scanner = Scanner(item)
            scanner.scan(self, 50)  # max links
            self._swap_bucket.extend(scanner.output)
            self._build_response(scanner.output, item, generation)

    def crawl(self):
        """Algorithm:
        For items in current bucket while gen < max gen
        if item not in scanned already, scan item --> swap bucket list; add item to scanned
        for items2 in swap bucket
        add scan item, items2 to response
        inc gen
        current bucket = scan bucket
        scan bucket = empty
        """

        g = 0
        print(Crawler.make_node(self._current_bucket[0]))
        while g <= self._generations:
            print("\nGeneration ", g)
            self._scan(g)
            self._current_bucket = self._swap_bucket
            self._swap_bucket = []
            g += 1


class GraphStorage(object):
    """The actual graph database storage"""

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)

    def close(self):
        self._driver.close()

    @staticmethod
    def make_obj(k_var, k_type, dict_prop) -> str:
        # does not use the $parameter format to create a custom node

        qry = "CREATE (" + k_var + ":" + k_type + "{"
        for k in dict_prop:
            qry += k + ":'" + dict_prop[k] + "',"
        qry = qry[:len(qry) - 1] + "}) return " + k_var + ";"
        return qry

    @staticmethod
    def make_rel(k_type1: str, k_prop1: str, k_val1: str,
                 k_type2: str, k_prop2: str, k_val2: str,
                 k_typer: str) -> str:
        # Beware: only matches string properties
        qry = "MATCH (n:" + k_type1 + "{" + k_prop1 + ": '" + k_val1 + "'}), (m:" + k_type2 + "{" + \
              k_prop2 + ": '" + k_val2 + "'}) CREATE (n)-[r:" + k_typer + "]->(m) return n, m, r;"
        return qry

    def run_command(self, query):
        with self._driver.session() as session:
            result = session.write_transaction(self._run_command, query)

    @staticmethod
    # TODO 4) fix here - what is returned? nothing for relationships?
    def _run_command(tx, query):
        result = tx.run(query)
        return result


class Demo:
    @classmethod
    def run(cls, url: str, gen: int, db: str, login: str, pwd: str):
        c = Crawler(url, gen, db, login, pwd)
        c.crawl()


Demo.run("https://www.zoso.ro/", 2, "bolt://localhost:7687", "gigifecali", "fecali")