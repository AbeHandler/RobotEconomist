'''
take a file list as input
process with spacy
write each file in list to a docbin in tmp/corpus/file.docbin
'''

import os
import sys

import spacy
from spacy.tokens import Doc, DocBin
from tqdm import tqdm as tqdm

def read_txt_file_and_process_with_spacy(filename: str) -> Doc:
    with open(filename, "r") as openfile:
        txt = openfile.read()
        doc = nlp(txt, disable=["parser", "ner"])
        doc._.filename = filename
    return doc

if __name__ == "__main__":

    nlp = spacy.load("en_core_web_md")
    Doc.set_extension("filename", default=None)
    doc_bin = DocBin(store_user_data=True)

    filelist = sys.argv[1]
    corpus = sys.argv[2]

    with open(filelist, "r") as list_of_files:
        msg: str = "running spacy on {}".format(filelist)
        for filename in tqdm(list_of_files, desc=msg):
            filename = filename.replace('\n', '')
            doc = read_txt_file_and_process_with_spacy(filename)
            doc_bin.add(doc)

    basename = os.path.basename(filelist)

    doc_bin.to_disk(f"tmp/{corpus}/proc/{basename}.docbin")

    # to load from disc do this
    # db = doc_bin.from_disk("tmp/nber/proc/{}.spacy.docbin".format(basename))

    # for doc in db.get_docs(nlp.vocab):
    #    print(doc._.filename)
