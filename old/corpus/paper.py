from dataclasses import dataclass
from typing import List

from src.corpus.section import Section


@dataclass(frozen=True)
class Paper:
    paper_id: str
    sections: List[Section]
    iv: str = None
    outcome: str = None
