from neo4j import GraphDatabase, basic_auth
import socket


class Movie_queries(object):
    def __init__(self, password):
        self.driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", password), encrypted=False)
        self.session = self.driver.session()
        self.transaction = self.session.begin_transaction()

    def q0(self):
        result = self.transaction.run("""
            MATCH (n:Actor) RETURN n.name, n.id ORDER BY n.birthday ASC LIMIT 3
        """)
        return [(r[0], r[1]) for r in result]

    def q1(self):
        result = self.transaction.run("""
        MATCH (a:Actor) -[:ACTS_IN]-> (m:Movie)
        RETURN a.name, COUNT(m.title) AS num_movies
        ORDER BY num_movies DESC, a.name ASC
        LIMIT 20

        """)
        return [(r[0], r[1]) for r in result]

    def q2(self):
        result = self.transaction.run("""
        MATCH (p:Person)-[:RATED]->(m:Movie) <-[:ACTS_IN]-(a:Actor) WITH m,
        COUNT(distinct a.name) as num_cast
        ORDER BY num_cast DESC LIMIT 1
        RETURN m.title, num_cast

        """)
        return [(r[0], r[1]) for r in result]

    def q3(self):
        result = self.transaction.run("""
        MATCH (d:Director) -[:DIRECTED]-> (m:Movie) WITH d,
        COUNT(distinct m.genre) as num_genre WHERE num_genre >= 2
        RETURN d.name, num_genre
        ORDER BY num_genre DESC, d.name ASC

        """)
        return [(r[0], r[1]) for r in result]

    def q4(self):
        result = self.transaction.run("""
        MATCH (bacon:Actor{name: "Kevin Bacon"})-[:ACTS_IN]->(m:Movie)<-[:ACTS_IN]-(a1:Actor)
        MATCH (a1:Actor)-[:ACTS_IN]->(m2:Movie)<-[:ACTS_IN]-(a2:Actor)
        WHERE a2 <> bacon AND NOT (bacon)-[:ACTS_IN]->()<-[:ACTS_IN]-(a2)
        RETURN DISTINCT a2.name
        ORDER BY a2.name
        """)
        return [(r[0]) for r in result]

if __name__ == "__main__":
    sol = Movie_queries("neo4jpass")
    print("---------- Q0 ----------")
    print(sol.q0())
    print("---------- Q1 ----------")
    print(sol.q1())
    print("---------- Q2 ----------")
    print(sol.q2())
    print("---------- Q3 ----------")
    print(sol.q3())
    print("---------- Q4 ----------")
    print(sol.q4())
    sol.transaction.close()
    sol.session.close()
    sol.driver.close()
