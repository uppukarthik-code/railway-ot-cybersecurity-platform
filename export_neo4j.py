from neo4j import GraphDatabase


def export_neo4j(
    topology,
    uri,
    user,
    password
):

    driver = GraphDatabase.driver(
        uri,
        auth=(user, password)
    )

    with driver.session() as session:

        # NODES

        for node in topology["nodes"]:

            session.run(
                """
                MERGE (n:Asset {
                    id: $id
                })

                SET
                    n.label = $label,
                    n.type = $type,
                    n.zone = $zone,
                    n.purdue = $purdue,
                    n.criticality = $criticality
                """,

                id=node["id"],
                label=node["label"],
                type=node["type"],
                zone=node["zone"],
                purdue=node.get(
                    "purdue_level"
                ),
                criticality=node.get(
                    "criticality"
                )
            )

        # EDGES

        for conn in topology["connections"]:

            session.run(
                """
                MATCH (a:Asset {
                    id: $source
                })

                MATCH (b:Asset {
                    id: $target
                })

                MERGE (a)-[:CONNECTS {
                    protocol: $protocol,
                    encrypted: $encrypted
                }]->(b)
                """,

                source=conn["source"],
                target=conn["target"],
                protocol=conn.get(
                    "protocol"
                ),
                encrypted=conn.get(
                    "encrypted"
                )
            )

    driver.close()