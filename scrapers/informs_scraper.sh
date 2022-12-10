
INFORMS_CODE="mnsc" # managment science
rm -rf $INFORMS_CODE.toc.txt && touch $INFORMS_CODE.toc.txt
rm -rf $INFORMS_CODE.urls.txt && touch $INFORMS_CODE.urls.txt

for i in $(pages -b https://pubsonline.informs.org/toc/$INFORMS_CODE/ -m 70); do
    for var in $(seq 1 4); do
        echo $i"/"$var >> $INFORMS_CODE.toc.txt
    done
done


while read p; do 
    echo $p |  stream -d 10 -v | urls | grep doi | uniq >> $INFORMS_CODE.urls.txt 
    echo $p
    wc -l $INFORMS_CODE.urls.txt
done < $INFORMS_CODE.toc.txt

mv $INFORMS_CODE.urls.txt management_science_paper_url_list.txt