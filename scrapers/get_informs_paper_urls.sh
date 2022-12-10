#!/usr/bin/env bash

# ./get_informs_paper_urls.sh mnsc 70
# make a list of URLS for an informs publication
# The example above shows a search for 70 urls from management science

INFORMS_CODE=$1 # "mnsc"
MAX_PAGES=$2
rm -rf $INFORMS_CODE.toc.txt && touch $INFORMS_CODE.toc.txt
rm -rf $INFORMS_CODE.urls.txt && touch $INFORMS_CODE.urls.txt

for i in $(pages -b https://pubsonline.informs.org/toc/$INFORMS_CODE/ -m $MAX_PAGES); do
    for var in $(seq 1 4); do
        echo $i"/"$var >> $INFORMS_CODE.toc.txt
    done
done


while read p; do 
    echo $p |  stream -d 10 -v | urls | grep doi | uniq >> $INFORMS_CODE.urls.txt 
    echo $p
    wc -l $INFORMS_CODE.urls.txt
done < $INFORMS_CODE.toc.txt

# mv $INFORMS_CODE.urls.txt management_science_paper_url_list.txt