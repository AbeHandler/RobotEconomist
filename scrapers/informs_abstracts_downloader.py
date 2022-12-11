import requests
import json
import sys
from bs4 import BeautifulSoup
from scrapingbee import ScrapingBeeClient
from tqdm import tqdm as tqdm


def get_abstract(url):

    client = ScrapingBeeClient(
        api_key='YF7YE0ZDWRP8SHXOQFMSCGJQDMQ2NMKC0GBYCXTNZD8W8MIYVRR5LRP3SA9UCBMG6Z6XNUGVNX1LIJV2')
    r = client.get(url, params={'render_js': 'False', 'premium_proxy': True})
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup.find_all("div", {"class": "abstractSection"})[0].text.replace("\n", " ").strip()


if __name__ == "__main__":
    informs_journal_code = sys.argv[1]  # e.g. mnsc
    with open(f"{informs_journal_code}.urls.txt", "r") as inf:
        urls = [i.replace("\n", "") for i in inf]
    with open(f"{informs_journal_code}.abstracts.jsonl", "w") as of:
        for urlno, url in tqdm(enumerate(urls), total=len(urls)):
            url = url.replace("\n", "")

            try:
                abstract = get_abstract(url)
            except:
                abstract = "failure"
            out = {"mnsc_id": url.split("/").pop(), "abstract": abstract}

            of.write(json.dumps(out) + "\n")
