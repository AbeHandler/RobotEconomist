import json
import os
import re
import shutil
from pathlib import Path
from typing import Iterator, List

from spacy.tokens import Doc, DocBin
from tqdm import tqdm as tqdm

from src.pipelines.pipeline_config import PipelineConfig


def _validate_input_abstracts_2_txt(
    path_to_corpus: str = "data/nber_abstracts",
) -> None:

    assert Path(
        path_to_corpus, "json"
    ).exists(), "Your raw data should be in a json directory"  # noqa: E501
    assert Path(
        path_to_corpus
    ).is_dir(), "Your raw data should be in a json directory"  # noqa: E501

    assert Path(
        path_to_corpus, "txt"
    ).exists(), "Expecting to write docs to a txt directory"  # noqa: E501
    assert Path(
        path_to_corpus
    ).is_dir(), "Expecting to write docs to a txt directory"  # noqa: E501


def get_valid_filename(s: str) -> str:
    s = str(s).strip().replace(" ", "_")
    return re.sub(r"(?u)[^-\w.]", "", s)[0:50]


def _reset_tmp_directory(
    config: PipelineConfig, steps: List[str] = ["splits", "proc", "spacy"]
) -> None:
    dirpath: Path = Path(config.tmp_dir, config.corpus)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath)

    for step in steps:
        path: Path = Path(config.tmp_dir, config.corpus, step)
        path.mkdir(parents=True, exist_ok=False)


def init_helper(config: PipelineConfig) -> None:
    corpus: str = config.corpus
    config = config
    for step in ["txt", "spacy", "extractions", "graphs", "similarities"]:
        os.system(f"mkdir -p data/{corpus}/{step}")

    _reset_tmp_directory(config)


def jsonl_2_txt(
    papers_filename: str = "papers.jsonl",
    text_field: str = "paperAbstract",
    id_field: str = "id",
    corpus: str = "s2orc_abstracts",
    data_directory: str = "data",  # almost always data, e.g. data/nber  # noqa: E501
) -> None:
    """
    In many cases raw papers are stored as jsonl. In this case,
    pull out text from a jsonl and write it to a txt files
    the text files will have filenames=paperids

    by convention the jsonl is held in a json directory as papers.jsonl
    and the txt files are written to a txt directory for spacy

    e.g. read from "data/nber/json/papers.jsonl"
    and write first line to "data/nber/txt/1.txt" etc
    """
    path_to_corpus = Path(data_directory, corpus).as_posix()
    _validate_input_abstracts_2_txt(path_to_corpus)

    text_directory: Path = Path(path_to_corpus, "txt")
    papers_file: Path = Path(path_to_corpus, "json", papers_filename)

    with open(papers_file.as_posix(), "r") as papers_file_handler:
        msg: str = "[*] Reading {}".format(papers_file.as_posix())
        for line in tqdm(papers_file_handler, desc=msg):
            one_paper_data: dict = json.loads(line)
            paper_id: str = one_paper_data[
                id_field
            ]  # json.load may read this is an int etc # noqa: E501
            paper_text: str = one_paper_data[text_field]
            output_path: str = Path(
                text_directory, get_valid_filename(paper_id)
            ).as_posix()

            # make sure the output path suffix is .txt
            output_path_suffix: str = output_path.split(".").pop()
            output_path = output_path.replace("." + output_path_suffix, ".txt")

            with open(output_path, "w") as of:
                of.write(paper_text)


def read_docs_from_disk(
    config: PipelineConfig,
) -> Iterator[Doc]:  # noqa E501
    """Spacy uses docbins to serialize many processed documents.
    But there are size limits to how big a docbin can get. So to
    read a big corpus from disc you need to read in more than 1 docbin
    from disc. Sometimes this takes too much memory so you need something
    that just returns a generator over docbins and docs in docbins"""

    files: List[Path] = list(Path(config.path_to_docbins).iterdir())
    files = [file for file in files if file.suffix == ".docbin"]

    for fn in tqdm(
        files,
        total=len(files),
        desc="[*] reading docs from {}".format(config.path_to_docbins),
    ):
        doc_bin: DocBin = DocBin(store_user_data=True).from_disk(str(fn))
        for doc in doc_bin.get_docs(config.vocab):
            yield doc


def read_doc_bin_from_disk(
    path_to_docbins: str = "data/nber/spacy/",
) -> DocBin:  # noqa E501
    """Spacy uses docbins to serialize many processed documents.
    But there are size limits to how big a docbin can get. So to
    read a big corpus from disc you need to read in more than 1 docbin
    from disc and merge them. This is a helper to do that

    :param path_to_docbins: where the docbins are stored on disc, defaults to "data/nber/spacy/"  # noqa E:501
    :type path_to_docbins: str, optional
    :return: a doc bin that merges the serialized docbins at path_to_docbins
    :rtype: DocBin
    """

    current_merged_doc_bin: DocBin = None  # type: ignore
    files: List[Path] = list(Path(path_to_docbins).iterdir())
    files = [file for file in files if file.suffix == ".docbin"]
    if len(files) == 0:
        msg: str = "Expected at least one docbin in {}".format(path_to_docbins)
        raise FileNotFoundError(msg)

    for fn in tqdm(
        files,
        total=len(files),
        desc="[*] loading docbins from {}".format(path_to_docbins),
    ):
        doc_bin: DocBin = DocBin(store_user_data=True).from_disk(str(fn))
        if current_merged_doc_bin is None:
            current_merged_doc_bin = doc_bin
        else:
            current_merged_doc_bin.merge(doc_bin)
    return current_merged_doc_bin
