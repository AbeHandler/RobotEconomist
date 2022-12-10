rm -rf mgmt.toc.txt && touch mgmt.toc.txt
rm -rf mgmt.urls.txt && touch mgmt.urls.txt

for i in $(pages -b https://pubsonline.informs.org/toc/mnsc/ -m 70); do
    for var in $(seq 1 4); do
        echo $i"/"$var >> mgmt.toc.txt
    done
done


while read p; do 
    echo $p |  stream -d 10 -v | urls | grep doi | uniq >> mgmt.urls.txt 
    echo $p
    wc -l mgmt.urls.txt
done < mgmt.toc.txt
