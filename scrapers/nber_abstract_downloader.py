import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm as tqdm

def get_abstract(paper: str):
    url = f"https://www.nber.org/papers/{paper}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find_all("div", {"class": "page-header__intro-inner"})[0].text.replace("\n", " ").strip()

with open("nber.abstracts.jsonl", "w") as of:
    for i in tqdm(range(1, 32000)):
        try:
            abstract = get_abstract(paper=f"w{i}")
        except:
            abstract = "failure"
        out = {"paper": i, "abstract": abstract}
        of.write(json.dumps(out) + "\n")