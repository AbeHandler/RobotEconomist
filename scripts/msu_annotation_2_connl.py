'''
Take data in the msu format and convert it to connl
'''

from typing import List
import spacy
import sys
from naveen.utils.readers import jsonlreader
from spacy.tokens.token import Token
from collections import namedtuple

Annotation = namedtuple('Annotation', 'start end label')
TokenRange = namedtuple('TokenRange', 'start end')
LabeledTokenSpan = namedtuple('LabeledTokenSpan', 'start end label')


def start_is_close(token: Token, offset: int, N_fudge_characters: int) -> bool:
    acceptable_range = range(offset - N_fudge_characters,
                             offset + N_fudge_characters + 1)
    return token.idx in acceptable_range


def end_is_close(token: Token, offset: int, N_fudge_characters: int) -> bool:
    acceptable_range = range(offset - N_fudge_characters,
                             offset + N_fudge_characters + 1)
    return token.idx + len(token) in acceptable_range


def annoation2tokenrange(annotation: Annotation,
                         tokens: List[Token]) -> TokenRange:
    start = next(t for t in tokens if start_is_close(
        t, annotation.start, 1))
    end = next(t for t in tokens if end_is_close(
        t, annotation.end, 1))
    return TokenRange(start.i, end.i + 1)


def can_resolve(annotation: Annotation,
                tokens: List[Token]) -> bool:
    if not any(t for t in tokens if start_is_close(t, annotation.start, 1)):
        return False
    if not any(t for t in tokens if end_is_close(t, annotation.end, 1)):
        return False
    return True


def doccano_output2_annotation(doccanooutput):
    if type(doccanooutput) == list: # if annoation is just entities/spans
        start_offset = doccanooutput[0]
        end_offset = doccanooutput[1]
        label = doccanooutput[2]
    if type(doccanooutput) == dict: # if annoation is entities and relations
        start_offset = doccanooutput['start_offset']
        end_offset = doccanooutput['end_offset']
        label = doccanooutput['label']

    return Annotation(start_offset, 
                      end_offset,
                      label)

def labels2token_spans(labels: list,
                       tokens: List[Token]) -> List[LabeledTokenSpan]:
    output: List[LabeledTokenSpan] = []
    for label in labels:
        annotation = doccano_output2_annotation(label)
        if can_resolve(annotation=annotation, tokens=tokens):
            indexes = annoation2tokenrange(annotation, tokens)
            span = LabeledTokenSpan(
                indexes.start, indexes.end, label=annotation.label)
            output.append(span)
        else:
            sys.stderr.write("issue")
    return output


def token2label(token: Token,
                labeled_token_spans: List[LabeledTokenSpan]) -> str:
    for span in labeled_token_spans:
        if token.i in range(span.start, span.end):
            return span.label
    return "O"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='process a file of doccano annotation to conll')
    parser.add_argument('--inputfile', '-i', dest='inputfile', default="data/msu/oren.jsonl")
    parser.add_argument('--field', '-f', dest='field', default="label")
    args =  parser.parse_args()

    outputfile = args.inputfile.replace('.jsonl', '.conll')

    nlp = spacy.load("en_core_web_sm")
    with open(outputfile, "w") as of:
        for linenumber, line in jsonlreader(args.inputfile):
            # print(line["text"])
            doc = nlp(line['text'])
            labels = line[args.field]
            labeled_token_spans = labels2token_spans(labels, [o for o in doc])
            for token in doc:
                label = token2label(token, labeled_token_spans)
                of.write(str(token) + "\t" + label + "\n")
            of.write("\n")
