import time
import pandas as pd
import os
import argparse
import json
import glob
import yaml
import os
import pathlib
import os
from jinja2 import Environment, FileSystemLoader
from json.decoder import JSONDecodeError


class Results2RecordIds(object):

    def url2recordid(self, url_: str):
        return url_.split("recordId=")[1].split("&")[0]

    def row2recordid(self, row: dict):
        url = row["links"]["v2-downloadLinks"][0]['url']
        export_link = self.url2recordid(url)
        return export_link
        
        
    def __init__(self, filename="results.jsonl"):
        self.id2pdfname = {}
        self.id2record = {}
        self.pdfid2id = {}
        with open(filename, "r") as inf:
            for o in inf:
                record = json.loads(o)
                id_ = record["id"]
                record_id = self.row2recordid(record)
                self.id2record[id_] = record
                self.id2pdfname[id_] = record_id
                self.pdfid2id[record_id] = id_

    def recordid2tite(self, recordid):
        recordid = self.pdfid2id[recordid]
        record = self.id2record[recordid]
        title = record["title"]["value"]
        title = title.replace("<mark>", "").replace("</mark>", "").replace(" ", "_").replace(".", "")
        return title

def make_curl(source="Marketing Science",
              year=2010,
              section="TX", # or AB
              query=["hedonic", "utilitarian"]):

    def make_query(words, section="AB"):
        backlash = "\\"
        none = ""
        quote = ""
        mappedwords = [f'''{section} ''' + none + quote + word + quote + none for word in words]
        return "("  + " AND ".join(mappedwords) + ")"

    with open("templates/paper.jinja") as f:
        template_str = f.read()

    template = Environment(loader=FileSystemLoader("templates/")).from_string(template_str)

    # example qry = '''(AB \"interview\" OR AB \"Interview\" OR AB \"Interviews\" OR AB \"interviews\")'''

    qry = str(make_query(words=query, section=section))
    source_string = f"(SO {source})"

    # (SO MIS Quarterly) AND (TX \"instrumental variable\")
    
    query = f"{qry} AND {source_string}"
    print(query)
    return template.render(query=query,
                           source=source,
                           year=str(year),
                           nextyear=str(year + 1))

def load_config(config):

    with open(config, "r") as stream:
        try:
            return(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)


def query_ebsco():
    '''
    to rerun this you need a new cookie in master_curl.sh by doing copy as curl
    see notes.md
    '''

    from random import shuffle
    papers = []
    with open("known_papers.txt", "r") as inf:
        for o in inf:
            papers.append(o.replace('\n', ''))

    papers = [p for p in papers if len(p) > 0]

            
    for ino, paper in enumerate(papers):             
        with open("templates/paper.jinja", "r") as inf:
            txt = inf.read()
            txt = txt.replace("PAPER", paper)
            txt = txt.replace("NUMBERR", str(ino))
            
            with open(f"curls/{ino}", "w") as of:
                of.write(txt)

    os.system("find curls | xargs chmod +x")

    os.system("find curls -type f | parallel '{}'")


def process_query():
    '''
    Process the downloaded data by making a big results.jsonl file
    '''
    print("[*] Processing query to results.jsonl ... ")
    out = []
    for fn in glob.glob('output/*'):
        with open(fn) as inf:
            try:
                if os.stat(fn).st_size > 0:
                    ou = json.load(inf)
                    if len(ou["search"]["items"]) < 4:
                        print('note, missing', fn)
                    for i in ou["search"]["items"]:
                        out.append(i)
            except JSONDecodeError:
                print(fn)

    print(f"[*] Processing {len(out)} results")
    with open('results.jsonl', "w") as of:
        for o in out:
            of.write(json.dumps(o) + '\n')

def whitelist_data(whitelist):
    new = []
    with open(whitelist, "r") as inf:
        source_whitelist = [o.replace("\n", "") for o in inf]
    with open('results.jsonl', "r") as inf:
        for o in inf:
            o = json.loads(o)
            if "source" in o.keys():
                if o["source"] in source_whitelist:
                    new.append(o)
            else: # TODO cleanup and do real logging
                print("Warning no source")
    with open('results.jsonl', "w") as of:
        for i in new:
            of.write(json.dumps(i) + "\n")


def get_download_script(id_, title):
    with open("templates/paperdownloader.jinja", "r") as inf:
        script = inf.read()
        script = script.replace('RECORDID', id_).replace("TITLE", title)
    return script


def download_papers():
    '''This function:
        (1) makes a TODO list for pdfs that have not been auto downloaded yet
        (2) makes scripts in downloadscripts which auto download pdfs (if possible)
    '''

    mapper = Results2RecordIds()

    for dir_ in ["downloadscripts"]:
        os.system(f"rm -rf {dir_}")
        try:
            os.mkdir(dir_)
        except FileExistsError:
            pass

    cmd = "cat results.jsonl | jq | grep recordId | grep pdf | grep v2-pdf | grep intent=download  | awk -F':' '{print $2}' | awk -F'=' '{print $2}' | awk -F'&' '{print $1}' > tmp/todo.txt"

    os.system(cmd)

    with open("tmp/todo.txt", "r") as inf:
        for o in inf:
            o = o.replace("\n", "")
            title = mapper.recordid2tite(o)
            script = get_download_script(o, title)
            with open("downloadscripts/" + o + ".sh", "w") as of:
                of.write(script)

    ### these scrips will auto download the pdf if possible
    os.system("chmod +x downloadscripts/*")

    os.system('find downloadscripts | parallel -j 1 "./{}"')


def analyze_data():
    '''analyze the search results'''

    df = pd.read_json("results.jsonl", lines=True)
    df["source"] = df["source"].apply(lambda x: x.replace("<mark>", "").replace("</mark>", ""))
    df = df[~df["source"].isnull()]
    df["yr"] = df["publicationDate"].apply(lambda x: str(x)[0:4])
    df["count"] = 1
    df = df.rename(columns={0:"count"})
    df = df[["source", "yr", "count"]]
    df = df.groupby(['source']).sum("count").reset_index()
    df = df.sort_values("count")
    df.to_csv("analysis.csv", index=False)



def init():
    print("[*] Initializing ... ")
    for dir_ in ["output", "curls"]:
        os.system(f"rm -rf {dir_}")
        try:
            os.mkdir(dir_)
        except FileExistsError:
            pass

    for file in ["results.jsonl", "results.csv"]:
        if os.path.isfile(file):
            print(f"removing {file}")
            os.remove(file)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--q", "-query", dest="query", action=argparse.BooleanOptionalAction, required=False, help="Do the search and download the query data")
    parser.add_argument("-p", "--p", "-process", dest="process", action=argparse.BooleanOptionalAction, required=False, help="Process downloaded data")
    parser.add_argument("-c", "--c", "-config", dest="config", help="Config file", required=True) #  e.g., config/hedonic.yaml
    parser.add_argument("-d", "--d", "-download", action=argparse.BooleanOptionalAction, dest="download", help="Download the papers?", required=False) #  e.g., config/hedonic.yaml
    parser.add_argument("-i", "--i", "-init", action=argparse.BooleanOptionalAction, dest="init", help="Call this before anything")


    # often ebsco is too permissive, use a whitelist
    parser.add_argument("-w", "--w", "-whitelist", dest="whitelist", action=argparse.BooleanOptionalAction, help="Apply a boolean whitelist specified in config") #  e.g., config/hedonic.yaml
    parser.add_argument("-a", "--a", "-analyze", dest="analyze", action=argparse.BooleanOptionalAction, help="Run analyze data") #  e.g., config/hedonic.yaml


    args = parser.parse_args()
    config = load_config(args.config)




    if args.init:
        init()

    if args.query:
        query_ebsco()

    if args.process:
        process_query()

    if args.download:
        download_papers()

    import os; os._exit(0)



    if args.whitelist:
        whitelist_data(config["whitelist"])

    if args.analyze:
        analyze_data()


