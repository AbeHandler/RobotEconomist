#!/usr/bin/env bash

# ./download_informs_papers.sh mnsc
# download the 
# The example above shows a search for 70 urls from management science

INFORMS_CODE=$1 # "mnsc"


while read p; do 
    echo $p |  stream -d 10 -v | urls | grep doi | uniq >> $INFORMS_CODE.urls.txt 
    echo $p
    wc -l $INFORMS_CODE.urls.txt
done < $INFORMS_CODE.toc.txt

# mv $INFORMS_CODE.urls.txt management_science_paper_url_list.txt