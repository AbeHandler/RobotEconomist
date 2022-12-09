jq ".title | .value" ivis.results.jsonl > titles.txt 
jq ".abstract | .value" ivis.results.jsonl > abstract.txt 
jq ".id" ivis.results.jsonl | tr -d '"'  > ids.txt 
paste abstract.txt ids.txt titles.txt > ivis.tsv
rm abstract.txt ids.txt titles.txt 
