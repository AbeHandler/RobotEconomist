import sys
import json

# data/rain/Abiona.json
with open(sys.argv[1], "r") as inf:
    dt = json.load(inf)
    ou = {}
    ou["id"] = sys.argv[1].split("/").pop()
    ou["text"] = dt["abstract"]
    ou["label"] = []

with open("data/doccano/abstracts.doccano.jsonl", "a") as of:
    of.write(json.dumps(ou) + "\n")
