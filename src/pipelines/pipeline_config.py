from dataclasses import dataclass
from pathlib import Path
from typing import List

import spacy
from spacy.vocab import Vocab


@dataclass
class PipelineConfig:
    corpus: str
    clear_cache: bool = True
    data_dir: str = "data"
    extractions_basename: str = "rulebased.extractions.jsonl"
    similarities_basename: str = "similarities.jsonl"
    index_directory: str = "tmp/indexes"
    tmp_dir: str = "tmp"
    include_similarities: bool = True  # include similarities in graph?
    docs_filename: str = "papers.jsonl"  # the jsonl file that holds input docs
    docs_text_field: str = (
        "paperAbstract"  # the field in jsonl that holds variables  # noqa: E501
    )
    docs_id_field: str = "id"  # the field in jsonl that holds the id

    graphs_dir: str = "graphs"
    txt_dir: str = "txt"
    spacy_dir: str = "spacy"
    extractions_dir: str = "extractions"
    similarities_dir: str = "similarities"

    spacy_model: str = "en_core_web_md"

    kdt_index_basename: str = "kdt_index.p"

    # if true, then use semantic similarities in the graph
    # This means try to say that 'violence' \approx 'crime' etc.
    # this setting will likely lead to greater recall at the expense of prec.
    use_semantic_similarities: bool = True

    bucket_name = "abha4861iv"
    bucket_url: str = "https://abha4861iv.s3.amazonaws.com/"
    
    # run the pipeline in debug mode?
    debug_mode: bool = False
    debug_max: int = 100

    def __post_init__(self) -> None:
        self.directories: List[str] = [
            self.graphs_dir,
            self.txt_dir,
            self.spacy_dir,
            self.extractions_dir,
            self.similarities_dir,
        ]

        self.vocab: Vocab = spacy.load(self.spacy_model).vocab

        self.path_to_docbins: Path = Path(
            self.data_dir, self.corpus, self.spacy_dir
        )

        self.path_to_rule_based_extractions: Path = Path(
            self.data_dir,
            self.corpus,
            self.extractions_dir,
            "rulebased.extractions.jsonl",
        )

        self.path_to_phrases: Path = Path(
            self.data_dir, self.corpus, self.extractions_dir, "phrases.jsonl"
        )

        self.extractions_path = Path(
            self.data_dir,
            self.corpus,
            self.extractions_dir,
            self.extractions_basename,
        )


if __name__ == "__main__":
    config = PipelineConfig(corpus="test")
    print(config)
