from pathlib import Path


def get_path_to_graph(cached_extractions_directory: str = "dags",
                      library: str = "nber",
                      graph_type: str = ".rulebased.extractions.jsonl.nxdigraph.json") -> Path:  # noqa: E501
    return Path(cached_extractions_directory,
                library + graph_type)
