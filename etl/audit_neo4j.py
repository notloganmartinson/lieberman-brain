from neo4j import GraphDatabase

URI = "***REMOVED***"
AUTH = ("***REMOVED***", "***REMOVED***")

def run_audit():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            # 1. Total Concept nodes and relationships
            print("--- Graph Size ---")
            result = session.run("MATCH (n:Concept) RETURN count(n) AS concept_count")
            print(f"Total Concept nodes: {result.single()['concept_count']}")
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS rel_count")
            print(f"Total relationships: {result.single()['rel_count']}")
            print()
            
            # 2. Embedding check
            print("--- Embeddings ---")
            result = session.run("MATCH (n:Concept) WHERE n.embedding IS NOT NULL RETURN n.id AS id, size(n.embedding) AS dim LIMIT 5")
            has_embeddings = False
            for record in result:
                has_embeddings = True
                print(f"Node ID: {record['id']}, Embedding dimension: {record['dim']}")
            if not has_embeddings:
                print("No embeddings found on Concept nodes!")
            print()

            # 3. Top 5 most connected nodes
            print("--- Top 5 Connected Nodes ---")
            result = session.run("""
            MATCH (n)-[r]-()
            RETURN coalesce(n.id, n.name, elementId(n)) AS id, count(r) AS degree
            ORDER BY degree DESC
            LIMIT 5
            """)
            for record in result:
                print(f"Node ID: {record['id']}, Degree: {record['degree']}")
            print()

            # 4. Sample 3 random edges
            print("--- Sample Edges ---")
            result = session.run("""
            MATCH (s)-[r]->(t)
            WITH s, r, t, rand() AS random
            ORDER BY random
            LIMIT 3
            RETURN labels(s) AS source_labels, type(r) AS rel_type, labels(t) AS target_labels, r.justification AS justification
            """)
            for i, record in enumerate(result):
                print(f"Edge {i+1}:")
                print(f"  Source Labels: {record['source_labels']}")
                print(f"  Target Labels: {record['target_labels']}")
                print(f"  Relationship Type: {record['rel_type']}")
                print(f"  Justification: {record['justification']}")
            print()

if __name__ == "__main__":
    run_audit()
