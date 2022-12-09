import glob 
import json
import os

for fn in glob.glob("nber_abstracts/json/*"):
	print(fn)
	basename = os.path.basename(fn).replace(".jsonl", ".txt")
	with open(fn, 'r') as paper_sections:
		for section in paper_sections:
			section = json.loads(section)
			if section['section_name'] == "abstract":
				with open("nber_abstracts/txt/" + basename, "w") as of:
					of.write(json.dumps(section["section_text"]))