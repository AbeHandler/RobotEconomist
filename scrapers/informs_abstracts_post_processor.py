import json
import os
import sys
from bs4 import BeautifulSoup



code = sys.argv[1] # e.g. "mnsc"
with open(f"{code}.abstracts.jsonl", "r") as inf:
    with open(f"clean.{code}.abstracts.jsonl", "w") as of:
        for i in inf:
            i = json.loads(i)
            soup = BeautifulSoup(i["html"], 'html.parser')
            text = soup.text
            id_ = i["url"].split("/").pop()
            out = {f'{code}_paper_id': id_, "abstract": text}
            of.write(json.dumps(out) + "\n")
os.system(f"mv clean.{code}.abstracts.jsonl code.abstracts.jsonl")