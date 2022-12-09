from pathlib import Path
from typing import List

from jinja2 import Template
from rich.color_triplet import ColorTriplet
from rich.console import Console
from rich.terminal_theme import SVG_EXPORT_THEME
from spacy.tokens import Doc, DocBin
from spacy.vocab import Vocab
from tqdm import tqdm as tqdm

from src.audit.abstract_possible_violation import PossibleViolation
from src.audit.auditor import Auditor
from src.audit.violation_hunter import ViolationHunter
from src.extractors.heuristic_extractor import HeuristicExtractor
from src.graph_builders.helpers import get_path_to_graph
from src.pipelines.helpers import read_doc_bin_from_disk
from src.pipelines.pipeline_config import PipelineConfig
from src.printers.extraction_printer import ExtractionPrinter  # noqa: E501
from src.printers.filesystem_document_provider import (  # noqa: E501
    FilesystemDocumentProvider,
)
from src.printers.violation_printer import ViolationPrinter
from src.publish.aws_helper import AwsHelper

SVG_EXPORT_THEME.background_color = ColorTriplet(252, 252, 252)
SVG_EXPORT_THEME.foreground_color = ColorTriplet(0, 0, 0)


if __name__ == "__main__":

    config = PipelineConfig(corpus="ivis")

    path_to_doc_bins = config.path_to_docbins

    vocab: Vocab = config.vocab

    Doc.set_extension("filename", default=None)

    db: DocBin = read_doc_bin_from_disk(path_to_doc_bins.as_posix())

    path_to_graph: Path = Path("src") / get_path_to_graph(library="ivis")
    auditor = Auditor(graph_specification=path_to_graph.as_posix())

    he = HeuristicExtractor(vocab)
    hunter = ViolationHunter(
        auditor, distance_threshold=30, min_edges=2, extractor=he
    )  # noqa: E501

    doc_provider: FilesystemDocumentProvider = FilesystemDocumentProvider()
    extraction_printer: ExtractionPrinter = ExtractionPrinter(
        context=150, provider=doc_provider
    )  # noqa: E501
    violation_printer: ViolationPrinter = ViolationPrinter(extraction_printer)

    total_violations: int = 0

    for p in Path("reports").iterdir():
        p.unlink()

    helper = AwsHelper()

    for doc in tqdm(db.get_docs(vocab)):

        possible_violations: List[
            PossibleViolation
        ] = hunter.get_possible_violations(  # noqa: E501
            doc
        )  # noqa: E501

        if len(possible_violations) > 0:
            total_violations += len(possible_violations)

        blacklist = ["network"]
        output_name: str = Path(doc._.filename).stem
        svg_fn: str = f"https://s3.amazonaws.com/abha4861iv/{output_name}.svg"
        svg_fn: str = f"{output_name}.svg"  # for local use

        for possible_violation in possible_violations:

            if (
                possible_violation.instrument.text_of_extraction.lower()
                not in blacklist
            ):  # noqa: E501
                report: str = violation_printer.pre_print(possible_violation)

                console = Console(record=True)

                console.print(report)

                with open("templates/annotation.html.jinja", "r") as inf:
                    template = Template(inf.read())

                with open(f"reports/{output_name}.html", "w") as of:
                    of.write(
                        template.render(
                            svg_file=svg_fn,  # noqa: E501
                            id=output_name,
                        )
                    )

                console.save_svg(
                    f"reports/{output_name}.svg",
                    theme=SVG_EXPORT_THEME,
                    title=output_name,
                )

                # helper.publish_report(output_name)
