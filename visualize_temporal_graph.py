
import json
import textwrap
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import networkx as nx

# Load the knowledge graph generated from Buzz messages.
with open("knowledge_graph.json", encoding="utf-8") as f:
    data = json.load(f)

messages = sorted(data["messages"], key=lambda x: x["timestamp"])

if not messages:
    raise ValueError("No messages found in knowledge_graph.json")

COLORS = {
    "Alice": "#3979D1",
    "Bob": "#E39B32",
    "Charlie": "#2F9D75",
    "Unknown": "#888888",
}

# Fixed positions prevent the nodes from jumping as time changes.
all_graph = nx.Graph()

for message in messages:
    for relation in message["relations"]:
        all_graph.add_edge(relation["subject"], relation["object"])

positions = nx.spring_layout(
    all_graph, seed=12, k=1.8, iterations=250
)

# Adjust the two crowded central nodes.
if "CNN" in positions and "preprocessing" in positions:
    positions["CNN"][1] -= 0.16
    positions["preprocessing"][1] += 0.16

fig = plt.figure(figsize=(14, 9))
ax = fig.add_axes([0.06, 0.29, 0.88, 0.62])
slider_ax = fig.add_axes([0.17, 0.15, 0.66, 0.035])
prev_ax = fig.add_axes([0.33, 0.065, 0.13, 0.05])
next_ax = fig.add_axes([0.54, 0.065, 0.13, 0.05])

timeline = Slider(
    slider_ax,
    "Message",
    valmin=1,
    valmax=len(messages),
    valinit=1,
    valstep=1,
)

prev_button = Button(prev_ax, "Previous")
next_button = Button(next_ax, "Next")


def wrap_label(text):
    return "\n".join(textwrap.wrap(text, width=19))


def update_graph(message_number):
    step = int(message_number)
    ax.clear()

    visible_messages = messages[:step]
    graph = nx.MultiDiGraph()

    for message in visible_messages:
        for relation in message["relations"]:
            graph.add_edge(
                relation["subject"],
                relation["object"],
                relation=relation["relation"],
                speaker=relation["speaker_label"],
                status=relation["status"],
                timestamp=relation["timestamp"],
            )

    # Draw only concepts introduced up to the selected message.
    visible_positions = {
        node: positions[node]
        for node in graph.nodes
    }

    nx.draw_networkx_nodes(
        graph,
        visible_positions,
        ax=ax,
        node_size=3300,
        node_color="#D9EAF5",
        edgecolors="#45667C",
        linewidths=1.4,
    )

    labels = {
        node: wrap_label(node)
        for node in graph.nodes
    }

    nx.draw_networkx_labels(
        graph,
        visible_positions,
        labels=labels,
        font_size=9,
        font_weight="bold",
        ax=ax,
    )

    # Edges are colored by the person who contributed them.
    # Questions are dashed; assertions are solid.
    for source, target, key, attrs in graph.edges(
        keys=True, data=True
    ):
        color = COLORS.get(attrs["speaker"], COLORS["Unknown"])
        line_style = (
            "dashed" if attrs["status"] == "question" else "solid"
        )

        nx.draw_networkx_edges(
            graph,
            visible_positions,
            edgelist=[(source, target)],
            ax=ax,
            edge_color=color,
            style=line_style,
            width=2.8,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=22,
            node_size=3300,
            connectionstyle="arc3,rad=0.07",
        )

        # Put the relation label near the middle of the edge.
        nx.draw_networkx_edge_labels(
            graph,
            visible_positions,
            edge_labels={(source, target): attrs["relation"]},
            ax=ax,
            font_size=8,
            rotate=False,
            bbox={
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.85,
                "pad": 1,
            },
        )

    current = messages[step - 1]
    speaker = current["speaker_label"]
    timestamp = datetime.fromisoformat(
        current["timestamp"].replace("Z", "+00:00")
    ).strftime("%H:%M:%S UTC")

    ax.set_title(
        f"Buzz Temporal Knowledge Graph\n"
        f"Message {step} of {len(messages)}  |  "
        f"{speaker}  |  {timestamp}",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # Show the message that was added in this step.
    fig.texts.clear()
    fig.text(
        0.5,
        0.225,
        f'Latest message: {speaker}: {current["message"]}',
        ha="center",
        va="center",
        fontsize=10,
        wrap=True,
    )

    # Keep the viewing area consistent across snapshots.
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    if xs and ys:
        ax.set_xlim(min(xs) - 0.35, max(xs) + 0.35)
        ax.set_ylim(min(ys) - 0.35, max(ys) + 0.35)

    ax.axis("off")
    fig.canvas.draw_idle()


def previous(event):
    timeline.set_val(max(1, int(timeline.val) - 1))


def next_step(event):
    timeline.set_val(
        min(len(messages), int(timeline.val) + 1)
    )


timeline.on_changed(update_graph)
prev_button.on_clicked(previous)
next_button.on_clicked(next_step)

update_graph(1)
plt.show()
