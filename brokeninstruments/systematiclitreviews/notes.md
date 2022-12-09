### Running this

1. run locally with vpn turned on
2. You will need to right click copy as curl to get an updated cookie. Go to https://discovery.ebsco.com/ and do a search. Then right click copy as curl the line marked "search" on the network tab in chrome dev tools.
	- Note that there are two things marked search, use the top one. You should be able to just copy the cookie line in your copied curl into `templates/master_curl.jinja.sh` and `templates/paperdownloader.jinja` and it should work. 
		- You use the `filter` field in the network tab to make this easier
	- You can modify '\"' around the query to find literal matches
3. Write a `config/yours.yaml` file specifying the parameters for your search. **You should not have to make any changes to the jina template to do this**
 	- Set the section you want to search, e.g. `AB` for abstract of `TX` for text
 	- **Important** If you want to get literal matches the easiest thing is to modify config.yml and leave the jinja template **unmodified
4. Run `py main.py -i -c config/yours.yaml` to reset the directories; the config is a required arg
5. Run `py main.py -c config/instrumental.yaml -q -p` which includes flags to query and process the data
6. After downloading you ofen have to make a whitelist b/c the ebsco source param is too permissive. If you don't already have a source whitelist, a good way to do this is
`cat results.jsonl | jq .source | sort | uniq -c | sort -n > config/hedonic_whitelist.txt` then update your config w/ the right whitelist
7. To update `templates/paperdownloder.sh` do `cat results.jsonl | jq | grep recordId | grep pdf | grep v2-pdf | grep intent=download` and append one of thos urls to `https://discovery.ebsco.com/` to get the curl
