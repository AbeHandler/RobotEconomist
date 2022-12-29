
from random import shuffle
from random import randint
import json
import pandas as pd
import os 


cmd = '''cat keywords.yml| grep "-"    | awk -F"- " '{print $2}' > patterns.txt'''

os.system(cmd)
os.system("gunzip ../scrapers/mnsc.sentences.jsonl.gz -c  | grep -f patterns.txt > sents.jsonl")



with open("patterns.txt", "r") as inf:
    patterns = [o.replace("\n", "") for o in inf]

sents = []
with open("sents.jsonl", "r") as inf:
    for i in inf:
        i = json.loads(i)
        i['text'] = i["sent"]
        del i["sent"]
        sents.append(i)

def replace_target(sent, target):
    return sent.replace(target, "<b>" + target + "</b>")

for ino, i in enumerate(sents):
    target = next(j for j in patterns if j in i["text"])
    sents[ino]["target"] = target
    sents[ino]["text"] = replace_target(sents[ino]["text"], target)
    sents[ino]["code1"] = randint(11, 40)
    sents[ino]["code2"] = randint(11, 40)


df = pd.DataFrame(sents)

df = df.sample(frac = 1, random_state=42)

df[df["target"] == "productivity"].to_csv("productivity.csv", index=False)