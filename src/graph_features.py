import networkx as nx
import pandas as pd   

def extract_graph_features(df: pd.DataFrame, address: str) -> dict:
    if df.empty:
        return {"interaction_degree": 0, "unique_counterparties": 0, "graph_density": 0, "avg_tx_value_to_neighbors": 0}

    G = nx.Graph()
    for _, tx in df.iterrows():
        a = tx["from"].lower()
        b = tx["to"].lower()
        value = tx["value"]
        G.add_edge(a, b, weight=value)

    target = address.lower()
    features = {
        "interaction_degree": G.degree(target),
        "unique_counterparties": len(list(G.neighbors(target))),
        "graph_density": nx.density(G) if len(G) > 1 else 0,
        "avg_tx_value_to_neighbors": (
            sum(data["weight"] for _, _, data in G.edges(target, data=True)) / max(1, G.degree(target))
        )
    }
    return features