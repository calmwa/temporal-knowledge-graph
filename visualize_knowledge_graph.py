
import json
import networkx as nx
import matplotlib.pyplot as plt

with open("knowledge_graph.json", encoding="utf-8") as f:
    data = json.load(f)

graph = nx.MultiDiGraph()

for item in data["group_graph"]["relations"]:
    graph.add_edge(
        item["subject"],
        item["object"],
        label=item["relation"],
        speaker=item["speaker_label"],
        timestamp=item["timestamp"],
        status=item["status"],
    )

positions = nx.spring_layout(graph, seed=42)

plt.figure(figsize=(12, 8))

nx.draw_networkx_nodes(
    graph, positions,
    node_size=2600,
    node_color="lightblue"
)

nx.draw_networkx_labels(
    graph, positions,
    font_size=9
)

nx.draw_networkx_edges(
    graph, positions,
    arrows=True,
    arrowsize=18,
    edge_color="gray"
)

edge_labels = {
    (u, v): attrs["label"]
    for u, v, attrs in graph.edges(data=True)
}

nx.draw_networkx_edge_labels(
    graph, positions,
    edge_labels=edge_labels,
    font_size=8
)

plt.title("Group Knowledge Graph from Buzz Conversation")
plt.axis("off")
plt.tight_layout()
plt.savefig("group_knowledge_graph.png", dpi=200)
print("Saved group_knowledge_graph.png")

