# using neo4J

# from pyneo4j import GraphDatabase, Node -- not well documented
# graph = GraphDatabase(user='neo4j', password='bangkok1')

# does not match the book
# site poorly documented

from py2neo import Graph, Node, NodeMatcher, Relationship

g = Graph(password="bangkok1")

for x in range(10):
    n2 = Node("People", name='Gigi Fecali', age=78, sex='f', nid=x, occupation='macelar')
    r = Relationship((n2, n2), when='10')
    g.create(n2)

find = NodeMatcher(g)
# nodes = find.match(labels="People", properties=("name", 'gigi fecali'))
# can this do any matching based on relationships?

nodes = find.match("Person", name="Gigi Fecali")

for n in nodes:
    print(n)
    print(n["name"])
    print("\t", n["age"])


