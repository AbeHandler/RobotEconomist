import json
from pathlib import Path

from sqlitedict import SqliteDict
from tqdm import tqdm as tqdm


class Corpus(object):
    def __init__(self, path_to_metadata: Path):
        self.db = SqliteDict("tmp/" + self._cache_name(path_to_metadata))

    def build_cache(self, path_to_metadata: Path):
        total = sum(1 for i in open(path_to_metadata.as_posix()))
        with open(path_to_metadata.as_posix(), "r") as inf:
            for i in tqdm(inf, total=total):
                i = json.loads(i)
                self.db[i["paper_id"]] = i
        self.db.commit()

    def _cache_name(self, path_to_metadata) -> str:
        return path_to_metadata.as_posix().replace("/", "_")

    def load_metadata_one_time(self, path_to_metadata: Path) -> None:
        self.index = {}
        total = sum(1 for i in open(path_to_metadata.as_posix()))
        with open(path_to_metadata.as_posix(), "r") as inf:
            for i in tqdm(inf, total=total):
                i = json.loads(i)
                self.index[i["paper_id"]] = i

    """ at some point you may want to make a fancier cache"""

    def get(self, paperid):
        try:
            return self.db[paperid]
        except KeyError:
            msg = f"Could not file key={paperid}. Try running "
            msg = (
                msg + "corpus.build_cache(data/corpus/metadata/metadata.jsonl)"
            )
            msg = msg + " Or it could be a bad key"
            raise KeyError(msg)


if __name__ == "__main__":
    path = Path("data", "s2orcfull", "metadata", "metadata.jsonl")
    corpus = Corpus(path)
    # corpus.build_cache(path)
    print(corpus.get("159350887"))
