import glob
import json
from typing import List
from dataclasses import dataclass
from src.corpus.paper import Paper


@dataclass(frozen=True)
class Corpus:
    corpus_id: str
    papers: List[Paper]
