import shutil
from email.mime import base
from pathlib import Path
from re import I
from typing import List

from networkx import DiGraph
from rich.color_triplet import ColorTriplet
from rich.console import Console
from rich.terminal_theme import SVG_EXPORT_THEME
from tqdm import tqdm as tqdm

from src.audit.hypothetical_violation import HypotheticalViolation
from src.corpus import Corpus
from src.printers.path_report import PathReport
from src.printers.snippets_printer import SnippetsPrinter


class HypotheticalViolationsWriter(object):
    def __init__(
        self,
        hypothetical_violations: List[HypotheticalViolation],
        storage_directory: Path,
        G: DiGraph,
        path_to_metadata: Path,
        base_url="https://abha4861iv.s3.amazonaws.com/tmp/violation/{vno}.svg",
    ) -> None:
        self.hypothetical_violations = hypothetical_violations
        self.storage_directory = storage_directory

        shutil.rmtree(self.storage_directory.as_posix(), ignore_errors=True)
        self.G = G
        self.storage_directory.mkdir(parents=True, exist_ok=True)
        self.path_to_metadata = path_to_metadata
        self.base_url = base_url

    def write_violations(self):

        corpus: Corpus = Corpus(self.path_to_metadata)

        printer = SnippetsPrinter(self.G, corpus=corpus)

        paths = []

        for vno, violation in enumerate(self.hypothetical_violations):
            vertex_names = violation.path.get_vertex_names()
            report = violation.path.get_edge_size_report()
            link = self.base_url.format(vno=vno)
            paths.append(PathReport(text=report, link=link))

            console = Console(record=True)
            vertex_names = violation.path.get_vertex_names()
            report = printer.pre_print(vertex_names)
            console.print(report)

            output_path: str = self.storage_directory / f"{vno}.svg"
            console.save_svg(
                output_path,
                theme=SVG_EXPORT_THEME,
                title=str(vno),
            )

        print(f"wrote to {self.storage_directory.as_posix()}")
        with open(self.storage_directory / "index.html", "w") as of:
            with open("templates/index.jinja") as file_:
                template = Template(file_.read())
                of.write(template.render(results=paths))

        # aws s3 ls s3://abha4861iv | awk -F " " '{print $4}' | parallel 'aws s3 rm s3://abha4861iv/{}'
        # find tmp/violation -type f | parallel 'aws s3 cp {} s3://abha4861iv/{} --acl public-read'


from jinja2 import Template

if __name__ == "__main__":
    with open("templates/index.jinja") as file_:
        template = Template(file_.read())

    results = []

    r = PathReport(text="a3", link="https://www.nytimes.com/")
    print(template.render(results=[r]))
