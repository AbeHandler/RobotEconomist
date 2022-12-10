import spacy
import json
import argparse

from typing import List
from spacy.lang.en import English
from nber_abstract_downloader import get_docs
from json.decoder import JSONDecodeError


def get_docs(code: str):
    out = []
    errors = 0
    count = 0
    with open(f"{code}.abstracts.jsonl", "r") as inf:
        for ino, i in enumerate(inf):
            count += 1
            i = i.replace("\n", "")
            try:
                i = json.loads(i)
                out.append(i)
            except JSONDecodeError:
                errors += 1
    print(f"[*] loaded {count} with {errors} errors")
    return out


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-code', dest='code', help='e.g. nber or mnsc')
    args = parser.parse_args()

    docs = get_docs(args.code)

    nlp = English()  # just the language with no pipeline
    nlp.add_pipe("sentencizer")
    sentence_id = 0
    outfile = f"{args.ucode}.sentences.jsonl"
    with open(outfile, "w") as of:
        for dno, jsonline in enumerate(docs):
            doc = nlp(jsonline["abstract"])
            for sent in doc.sents:
                sentence_id += 1
                out = {"id": sentence_id, "sent": str(sent), f"{code}_paper_id": jsonline[f"{code}_paper_id"]}
                of.write(json.dumps(out) + '\n')

    print(f"[*] wrote {sentence_id} sentences to {outfile}")