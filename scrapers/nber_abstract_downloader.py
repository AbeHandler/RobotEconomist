import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm as tqdm

def get_abstract(paper: str):
    url = f"https://www.nber.org/papers/{paper}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.find_all("div", {"class": "page-header__intro-inner"})[0].text.replace("\n", " ").strip()

def get_docs():
    out = []
    with open("nber.abstracts.jsonl", "r") as inf:
        for i in inf:
            i = i.replace("\n", "")
            i = json.loads(i)
            abstract = i["abstract"]
            out.append(abstract)
    return out

if __name__ == "__main__":
    
    with open("nber.abstracts.jsonl", "w") as of:
        for i in tqdm(range(19480, 19500)):
            try:
                abstract = get_abstract(paper=f"w{i}")
            except:
                abstract = "failure"
            out = {"nber_paper_id": i, "abstract": abstract}
            of.write(json.dumps(out) + "\n")


    docs = get_docs()
    print(len(docs))