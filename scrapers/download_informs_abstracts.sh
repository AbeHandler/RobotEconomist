#!/usr/bin/env bash

# ./download_informs_papers.sh mnsc
# This script will download abstracts from informs 
# It assumes you already have a url list of articles to download, stored at $INFORMS_CODE.urls.txt (see make scrape for more) 

INFORMS_CODE=$1 # "mnsc"

rm -f $INFORMS_CODE.abstracts.jsonl && touch $INFORMS_CODE.abstracts.jsonl

echo $INFORMS_CODE.jsonl

while read p; do 
    echo $p
    echo $p |  stream -d 10  | pluck -a class -e div -v abstractSection >> $INFORMS_CODE.abstracts.jsonl
done < $INFORMS_CODE.urls.txt


python informs_abstracts_post_processor.py $INFORMS_CODE