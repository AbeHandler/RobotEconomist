import sys
import json
import phrasemachine
import spacy
import glob
from tqdm import tqdm
from itertools import combinations
from itertools import permutations
from spacy.tokens import Doc
from spacy.vocab import Vocab

nlp = spacy.load("en_core_web_sm")

def overlap(span1, span2):
    range1 = range(span1[0], span1[1])
    range2 = range(span2[0], span2[1])
    for r1 in range1:
        for r2 in range2:
            if r1 == r2:
                return True
    return False


def spanlen(span):
    range1 = range(span[0], span[1])
    return len(range1)

def ix2phrase(indexes, tokens):
    s, e = indexes
    return " ".join(tokens[s:e])

total = 0

out = []

for fn in tqdm(glob.glob("data/rain/*")):

    # data/rain/Abiona.json
    with open(fn, "r") as inf:
        dt = json.load(inf)
        ou = {}
        ou["id"] = fn.split("/").pop()
        ou["text"] = dt["abstract"]
        ou["label"] = []
        doc = nlp(ou["text"])  # Original Doc

        for sent in doc.sents:
            tokens = [token.text for token in sent]
            pos = [token.pos_ for token in sent]
            phrases = phrasemachine.get_phrases(tokens=tokens, minlen=2, maxlen=3, postags=pos, output=["counts", "token_spans"])

            remove_these = set()
            combos = [j for j in permutations(phrases["token_spans"], 2)]
            for combo in combos:
                span1, span2 = combo
                if overlap(span1, span2):
                    shorter = min(span1, span2, key=spanlen)
                    remove_these.add(shorter)
            keep_these = [o for o in phrases["token_spans"] if o not in remove_these]

            nouns = []

            for token in sent:
                if token.pos_ == "NOUN":
                    nouns.append(token.i)

            start = sent[0].i
            for permutation in permutations(nouns, 2):
                n1, n2 = permutation
                if abs(n1 - n2) < 6 and abs(n1 - n2) > 1:
                    
                    #print("***")
                    #print(sent)
                    v1 = tokens[n1 - start]
                    v2 = tokens[n2 - start]
                    #print(f"According to the sentence above, does {v1} affect {v2}")
            #print([ix2phrase(k, tokens) for k in keep_these])


            #$print("")
            #print("*", sent)
            for phrase in phrases["counts"]:
                #print(ix2phrase(phrase, tokens))
                total += 1
                s = sent
                q = f"This sentence says that something effects {phrase}?"
                out.append((q, s))

from random import shuffle
shuffle(out)

for q, s in out[0:100]:
    print("**")
    print(q, s)
