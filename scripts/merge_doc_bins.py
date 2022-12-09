"""
processing spacy on a file list makes lots of little docbin files, one per file
list

this script merges them into a few bigger docbins

spacy 3 won't let you have docbins that are too big so you have to do the merge
"""

import glob
import os
from pathlib import Path

from spacy.tokens import DocBin
from tqdm import tqdm as tqdm

from src.pipelines.helpers import read_docs_from_disk
from src.pipelines.pipeline_config import PipelineConfig


def get_output_filename(
    path_to_merged_doc_bins: str, total_bins_written_so_far: int, corpus: str
) -> str:

    output_template = corpus + ".{}.spacy.docbin"
    basename = output_template.format(total_bins_written_so_far)
    return str(Path(path_to_merged_doc_bins, basename))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    current_merged_doc_bin = None
    bins_since_last_write: int = 0
    total_bins_written_so_far: int = 0
    total_docs_in_all_bins: int = 0

    parser.add_argument(
        "--path-to-unmerged-doc-bins",
        required=True,
        dest="path_to_unmerged_doc_bins",
    )
    parser.add_argument(
        "--path-to-merged-doc-bins",
        required=True,
        dest="path_to_merged_doc_bins",
    )
    parser.add_argument("--corpus", dest="corpus", required=True)
    args = parser.parse_args()

    corpus = args.corpus

    # Remove old files
    for fn in glob.glob(args.path_to_merged_doc_bins + "/*"):
        print("deleting {}".format(fn))
        os.remove(fn)

    # Merge processed files
    for fn in tqdm(
        glob.glob(args.path_to_unmerged_doc_bins + "/*.docbin"),
        desc=f"merging {args.path_to_unmerged_doc_bins}/*docbin files",
    ):
        doc_bin = DocBin(store_user_data=True).from_disk(fn)
        if current_merged_doc_bin is None:
            current_merged_doc_bin = doc_bin
        else:
            current_merged_doc_bin.merge(doc_bin)

        bins_since_last_write += 1
        if bins_since_last_write > 30:
            output_filename = get_output_filename(
                args.path_to_merged_doc_bins,
                total_bins_written_so_far,
                corpus=corpus,
            )
            current_merged_doc_bin.to_disk(output_filename)
            total_docs_in_all_bins += len(current_merged_doc_bin)
            bins_since_last_write = 0
            current_merged_doc_bin = None
            total_bins_written_so_far += 1

    # write remainder to disk
    if current_merged_doc_bin is not None:
        output_filename = get_output_filename(
            args.path_to_merged_doc_bins,
            total_bins_written_so_far,
            corpus=corpus,
        )
        print("written", output_filename)
        current_merged_doc_bin.to_disk(output_filename)  # type: ignore
        total_docs_in_all_bins += len(current_merged_doc_bin)  # type: ignore

    count = 0
    config = PipelineConfig(args.corpus)
    for doc in read_docs_from_disk(config):
        count += 1

    assert total_docs_in_all_bins == count
    print("ok no erro")
