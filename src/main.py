import argparse
import os
from pathlib import Path
from typing import List

from networkx import DiGraph
from pkg_resources import resource_filename
from rich import print

from src.audit.auditor import Auditor
from src.audit.hypothetical_violation import HypotheticalViolation
from src.corpus import Corpus
from src.graph_builders.helpers import get_path_to_graph
from src.printers.abbreviated_printer import AbbreviatedPrinter
from src.printers.abstract_path_printer import AbstractPathPrinter
from src.printers.hypothetical_violations_writer import (
    HypotheticalViolationsWriter,
)
from src.printers.snippets_printer import SnippetsPrinter


def get_instrument_from_user() -> str:
    print("")
    print(" Please describe your instrument. For example, you might type: ")
    print("-  weather ")
    print("-  election day rain ")
    print("-  draft lottery ")
    print("-  judge fixed effects ")
    return input("Please describe your instrument ")


def get_outcome_from_user() -> str:
    print("")
    print(" Please describe your outcome. For example, you might type: ")
    print("-  voting ")
    print("-  political participation ")
    print("-  trade volume ")
    print("-  college graduation rates ")
    return input("Please describe your outcome ")


def _check_valid_library(path_to_causal_graph: Path) -> None:
    if not path_to_causal_graph.exists():
        msg = "No causal graph found. The most likely cause is you "
        msg = msg + "selected a library that is not supported. Try "
        msg = msg + "using the library nber or nber_abstracts"
        raise FileNotFoundError(msg)


def controls() -> None:

    msg = "Search for instruments"
    parser = argparse.ArgumentParser(msg)
    parser.add_argument("-m", "--max", dest="max", type=int, default=5)
    parser.add_argument(
        "-o", "--outcome", dest="outcome", required=True, type=str
    )
    parser.add_argument(
        "-library",
        "--library",
        dest="library",
        type=str,
        default="s2orcfull",
    )
    args = parser.parse_args()

    print(args)
    library: str = args.library
    outcome: str = args.outcome

    path_to_graph: str = resource_filename(
        __name__, str(get_path_to_graph(library=library))
    )

    auditor = Auditor(graph_specification=path_to_graph)

    violations: List[
        HypotheticalViolation
    ] = auditor.get_all_hypothetical_violations_to_outcome(outcome)
    violations = [o for o in violations if not o.is_only_semantic()]
    violations = [o for o in violations if not len(o.path.vertexes) < args.max]

    violations = [o for o in violations if o.total_semantic() < 3]
    violations = [o for o in violations if o.max_semantic_distance() < 30]

    violations.sort(key=lambda x: len(x.path.vertexes), reverse=True)

    printer = SnippetsPrinter(auditor.graph)  # needs corpus
    for violation in violations:
        vertex_names = violation.path.get_vertex_names()
        print(vertex_names)
        printer.print(vertex_names)


def iv() -> None:

    msg = "Search for instruments"
    parser = argparse.ArgumentParser(msg)
    parser.add_argument("-i", "--instrument", dest="instrument", type=str)
    parser.add_argument("-o", "--outcome", dest="outcome", type=str)
    parser.add_argument(
        "-c",
        default=False,
        dest="concision",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-library",
        "--library",
        dest="library",
        type=str,
        default="s2orcfull",
    )
    args = parser.parse_args()

    library: str = args.library
    instrument: str = args.instrument
    outcome: str = args.outcome

    path = Path("data", args.library, "metadata", "metadata.jsonl")
    corpus = Corpus(path)

    path_to_graph: str = resource_filename(
        __name__, str(get_path_to_graph(library=library))
    )

    try:
        _check_valid_library(Path(path_to_graph))
    except FileNotFoundError as e:
        print("[bold red]Error: [/bold red]" + str(e))
        os._exit(1)

    if instrument == "":
        instrument = get_instrument_from_user()
    if outcome == "":
        outcome = get_outcome_from_user()

    print("")
    print(f"- Your instrument is [bold]{instrument}\n")
    print(f"- Your outcome is [bold]{outcome}\n")

    # TODO say number in corpus below
    print(f"[green] Searching the papers from {library}\n")

    auditor = Auditor(graph_specification=path_to_graph)

    try:
        has_violation: bool = auditor.has_iv_violation(
            proposed_instrument=instrument,  # noqa: E501
            proposed_outcome=outcome,
        )  # noqa: E501

        if has_violation:

            G: DiGraph = auditor._load_graph(path_to_graph)

            if args.concision:
                printer: AbstractPathPrinter = AbbreviatedPrinter(G)
            else:
                printer = SnippetsPrinter(G, corpus)

            violations: List[
                HypotheticalViolation
            ] = auditor.get_all_hypothetical_violations_from_instrument_to_outcome(  # noqa E:501
                instrument, outcome
            )

            violations = [o for o in violations if not o.is_only_semantic()]

            for vno, violation in enumerate(violations):
                vertex_names = violation.path.get_vertex_names()
                printer.print(vertex_names)
            # print(len(violations))

            writer = HypotheticalViolationsWriter(
                violations,
                Path("tmp", "violation"),
                G,
                Path("data", library, "metadata", "metadata.jsonl"),
            )
            writer.write_violations()

        else:
            print("[*] No violations found")
    except AttributeError as e:
        print("[bold red] Error:[/bold red]" + str(e))


if __name__ == "__main__":
    # controls()
    iv()
