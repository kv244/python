import urllib.request
from bs4 import *
from urllib.parse import urljoin
import sqlite3 as sqlite
import re

# words can be removed, only using links

sql_comm = [
	"create table urllist(url)",
	"create table link(fromid integer, toid integer)",
	"create index urlidx on urllist(url)",
	"create index urltoidx on link(toid)",
	"create index urlfromidx on link(fromid)"
]

path = "/Users/julianpetrescu/Documents/collective/"


class Crawler:
	def __init__(self, dbname, dbg=False):
		self.con = sqlite.connect(path+dbname)
		self.dbname = path + dbname
		self.debug = dbg
		print("Using database: ", self.dbname)

	def __del__(self):
		self.con.close()

	def db_commit(self):
		self.con.commit()

	def get_entry_id(self, table, field, value, create_new = True):
		# self.sql_debug("getentryid")
		cur = self.con.execute("select rowid from %s where %s='%s'" % (table, field, value))
		res = cur.fetchone()
		if res is None:
			cur = self.con.execute("insert into %s(%s) values('%s')" % (table, field, value))
			# insets into wordlist
			return cur.lastrowid
		else:
			return res[0]

	def get_text_only(self, soup):
		v = soup.string
		if v is None:
			c = soup.contents
			result_text = ''
			for t in c:
				sub_text = self.get_text_only(t)
				result_text += sub_text + '\n'
			return result_text
		else:
			return v.strip()

	def separate_words(self, text):
		return [s.lower() for s in re.split(r'\W+', text) if s != '']

	def is_indexed(self, url):
		# self.sql_debug("isindexed")
		u = self.con.execute("select rowid from urllist where url = '" + url + "'").fetchone()
		if u is not None:
			v = self.con.execute('select * from wordlocation where urlid = ' +str (u[0])).fetchone()
			if v is not None:
				return True
		return False

	def add_link_ref(self, url_from, url_to, link_text):
		print("AddLinkRef: ", url_from + "->" + url_to + " [" + link_text + "]")

	def crawl(self, pages, depth = 2):
		for i in range(depth):
			new_pages = set()

			for page in pages:
				print("\nOpening page: ", page)
				try:
					c = urllib.request.urlopen(page)
				except:
					print("\tcan't open")
					continue
				soup = BeautifulSoup(c.read())

				links = soup('a')
				# print("*", links)
				for link in links:
					print("!", link.attrs)  # href, title
					if 'href' in dict(link.attrs):
						url = urljoin(page, link['href'])  # https ...
						print("!!", url)
						if url.find("'") != -1:
							continue
						url = url.split('#')[0]
						print("\n\t\tUrl found: ", url)
						if url[0:4] == 'http' and not self.is_indexed(url):
							new_pages.add(url)
							print("URL to index as: ", hash(url))
						else:
							print("Url seems indexed: ", url)
							print(self.is_indexed(url))
						link_text = self.get_text_only(link)
						print("!!!", link_text)  # this is the text of the link
						self.add_link_ref(page, url, link_text)
						# does nothing
				self.db_commit()
			pages = new_pages

	def create_index_tables(self):
		# c = self.con
		for sql in sql_comm:
			self.con.execute(sql)
			print(sql)

		self.db_commit()
		# self.sql_debug("createindextables")

	def sql_debug(self, rtn=""):
		if self.debug is False:
			return
		sqls = "SELECT * FROM sqlite_master WHERE type='table'"
		print("** SQL Debug ", rtn)
		print("\nTables in " + self.db_name + "\n")
		cur = self.con.execute(sqls)
		res = cur.fetchall()

		for row in res:
			print(row)


class Searcher:
	def __init__(self, dbname):
		self.con = sqlite.connect(dbname)

	def __del__(self):
		self.con.close()

	def get_match_rows(self, q):
		field_list = 'wo.urlid'
		table_list = ''
		clause_list = ''
		word_ids = []

		words = q.split(' ')
		table_number = 0

		for word in words:
			word_row = self.con.execute(
				"select rowid from wordlist where word='%s'" %(word)).fetchone()
			if word_row is not None:
				word_id = word_row[0]
				word_ids.append(word_id)
				if table_number > 0:
					table_list += ', '
					clause_list += ' and '
					clause_list += 'w%d.urlid=w%d.urlid and ' % (table_number - 1, table_number)
				table_list += 'wordlocation w%d' % table_number
				field_list += ', w%d.location ' % table_number
				clause_list += 'w%d.wordid=%d' % (table_number, word_id)
				table_number += 1
			full_query = 'select %s from %s where %s ' (field_list, table_list, clause_list)
			cur = self.con.execute(full_query)
			rows = [row for row in cur]
			return rows, word_ids