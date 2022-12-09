from src.audit.possible_document_violation import PossibleDocumentViolation
from src.printers.edge_printer import EdgePrinter
from src.printers.extraction_printer import ExtractionPrinter


class ViolationPrinter(object):
    def __init__(self, extraction_printer: ExtractionPrinter) -> None:
        self.extraction_printer = extraction_printer

    def pre_print(self, possible_violation: PossibleDocumentViolation) -> str:

        out: str = ""

        out = (
            out
            + f"\t Instrument: [bold red] {possible_violation.instrument.text_of_extraction}[/bold red]\n"
        )  # noqa: E501

        out = out + "\n"

        out = (
            out
            + self.extraction_printer.pre_print(
                possible_violation.instrument, color="red"
            )
            + "\n"
        )  # noqa: E501

        out = (
            out
            + f"\n\t Outcome: [bold red] {possible_violation.outcome.text_of_extraction} [/bold red] \n"
        )  # noqa: E501

        out = out + "\n"

        out = (
            out
            + self.extraction_printer.pre_print(
                possible_violation.outcome, color="red"
            )
            + "\n"
        )  # noqa: E501

        out = out + "\n"

        out = out + "\t Possible violation: \n\n"

        edge_printer = EdgePrinter()
        for edge in possible_violation.path.edges:
            out = out + edge_printer.pre_print(edge=edge) + "\n"

        return out
