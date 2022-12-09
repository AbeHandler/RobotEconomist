import argparse
from email.policy import default
from re import I
import ipdb
from typing import List
from regex import W
import spacy
import glob
import os
import phrasemachine
import json
from tqdm import tqdm
from spacy.tokens import DocBin
from collections import defaultdict


def get_docs(pattern="data/nber/*txt", limit=None):
    texts = []
    c = 0
    for fn in glob.glob(pattern):
        if limit is not None and c > limit:
            break
        with open(fn, "r") as inf:
            txt = inf.read()
            doc = nlp(txt)
            c += 1
            yield doc


if __name__ == "__main__":
    os.system("mkdir -p data/nber/spacy")

    parser = argparse.ArgumentParser(description='Short sample app')

    parser.add_argument('-limit', '--limit', action="store",
                        type=int, dest="limit")

    parser.add_argument('-minthresh', '--minthresh', action="store",
                        type=int, default=1, dest="minthresh")

    args = parser.parse_args()
    print(args)

    nlp = spacy.load("en_core_web_sm", exclude=[
                     "ner", "parser"])
    print(nlp.pipe_names)

    counts = defaultdict(int)
    ivcounts = defaultdict(int)
    papercounts = defaultdict(int)

    for doc in tqdm(get_docs(limit=args.limit)):
        tokens = [token for token in doc]
        tokens_s = [str(o) for o in doc]
        pos = [str(token.pos_) for token in doc]

        all_phrases = phrasemachine.get_phrases(
            tokens=tokens_s, postags=pos, output="token_spans")["token_spans"]

        instrument_words: List[str] = ["instrument", "instrumental"]
        iv_toks = [t for t in tokens if str(t).lower() in instrument_words]

        for phrase in all_phrases:
            s, e = phrase
            phrase_linear = " ".join(tokens_s[s:e])
            counts[phrase_linear] += 1

        WINDOW = 150
        phrases_all = set()
        for tok in iv_toks:
            s = max(0, tok.i - WINDOW)
            e = min(tok.i + WINDOW, len(tokens))
            tokens_small = tokens[s:e]
            pos_small = pos[s: e]
            all_phrases = phrasemachine.get_phrases(
                tokens=tokens_small, postags=pos_small, output="token_spans")["token_spans"]

            for phrase in all_phrases:
                s, e = phrase
                phrase_linear = " ".join([str(i) for i in tokens_small[s:e]])
                phrases_all.add(phrase_linear)
                ivcounts[phrase_linear] += 1
        for p in phrases_all:
            papercounts[p] += 1

    #print(counts['unrestricted model'])
    #print(ivcounts['unrestricted model'])
    print("finished counting")
    probs = {k: counts[k]/sum(counts.values())
             for k, v in counts.items() if papercounts[k] > args.minthresh}

    ivprobs = {k: ivcounts[k]/sum(ivcounts.values())
               for k, v in ivcounts.items() if papercounts[k] > args.minthresh}

    with open("data/interim/probs.json", "w") as of:
        json.dump(probs, of)

    with open("data/interim/ivprobs.json", "w") as of:
        json.dump(ivprobs, of)

    with open("data/interim/probs.json", "r") as inf:
        probs = json.load(inf)

    with open("data/interim/ivprobs.json", "r") as inf:
        ivprobs = json.load(inf)

    lifts = {}
    for iv in ivprobs.keys():
        n = ivprobs[iv]
        d = probs[iv]
        lifts[iv] = n/d

    with open("data/interim/lifts.json", "w") as of:
        lifts = [(k, v) for k, v in lifts.items()]
        lifts.sort(key=lambda x: x[1], reverse=True)
        for l in lifts:
            a, b = l
            of.write("{},{}\n".format(a, b))
