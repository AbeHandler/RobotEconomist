gunzip -c mnsc.sentences.jsonl.gz| shuf | jq .sent | grep -f seeds.txt -i -w  | shuf > yes.txt
gunzip -c mnsc.sentences.jsonl.gz| shuf | head -1000 > no.txt
gunzip -c mnsc.sentences.jsonl.gz| jq .sent | shuf > all_data.txt