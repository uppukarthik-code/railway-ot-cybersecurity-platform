from neo4j import GraphDatabase

URI = "neo4j+s://a68d6713.databases.neo4j.io"

USER = "a68d6713"

PASSWORD = "6ZmtWjVohj1j09C6tEDr5_14GAEdaxPh3JYdvWu-xf0"


driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)

with driver.session() as session:

    result = session.run(
        "RETURN 'Neo4j Connected' AS msg"
    )

    print(
        result.single()["msg"]
    )

driver.close()