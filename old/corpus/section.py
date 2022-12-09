from dataclasses import dataclass


@dataclass(frozen=True)
class Section:
    title: str
    text: str
    paper_id: str
