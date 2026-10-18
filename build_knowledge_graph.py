
import csv
import re
import json
from collections import defaultdict
from pathlib import Path

INPUT = Path("kg_messages.csv")
OUTPUT = Path("knowledge_graph.json")

# Simple concept and relationship extraction rules for this demo.
# A later version can replace these rules with an NLP model.
RULES = [
    (r"\bCNNs?\b.*recognize patterns", "CNN", "recognizes", "visual patterns"),
    (r"\bCNNs?\b.*detect tumors", "CNN", "could_detect", "tumors"),
    (r"preprocess.*before training", "preprocessing", "precedes", "CNN training"),
    (r"preprocessing.*resizing", "preprocessing", "includes", "resizing"),
    (r"preprocessing.*normalization", "preprocessing", "includes", "normalization"),
    (r"preprocessing.*improves.*consistency", "preprocessing", "improves", "training-data consistency"),
]

events = []
participants = defaultdict(lambda: {"concepts": set(), "relations": []})
group_concepts = set()
group_relations = []

with INPUT.open(newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        raw = row["content"].strip()

        # Demo-only speaker labels; these are NOT authenticated Buzz identities.
        match = re.match(r"^(Alice|Bob|Charlie):?\s+(.+)$", raw)
        speaker = match.group(1) if match else "Unknown"
        message = match.group(2) if match else raw

        is_question = message.endswith("?")
        extracted = []

        for pattern, subject, relation, obj in RULES:
            if re.search(pattern, message, re.IGNORECASE):
                fact = {
                    "subject": subject,
                    "relation": relation,
                    "object": obj,
                    "status": "question" if is_question else "assertion",
                    "timestamp": row["created_at"],
                    "speaker_label": speaker,
                }
                extracted.append(fact)
                participants[speaker]["concepts"].update([subject, obj])
                participants[speaker]["relations"].append(fact)
                group_concepts.update([subject, obj])
                group_relations.append(fact)

        events.append({
            "timestamp": row["created_at"],
            "buzz_author_id": row["author_id"],
            "speaker_label": speaker,
            "message": message,
            "relations": extracted,
        })

result = {
    "messages": events,
    "individual_graphs": {
        name: {
            "concepts": sorted(data["concepts"]),
            "relations": data["relations"],
        }
        for name, data in participants.items()
    },
    "group_graph": {
        "concepts": sorted(group_concepts),
        "relations": group_relations,
    },
}

OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print(f"Processed {len(events)} messages")
print(f"Extracted {len(group_relations)} relationships")
print(f"Saved to {OUTPUT}")
for name, data in result["individual_graphs"].items():
    print(f"{name}: {len(data['relations'])} relationships")

