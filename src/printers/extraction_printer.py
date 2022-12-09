

from src.extractors.extraction import Extraction
from src.printers.abstract_document_provider import AbstractDocumentProvider


class ExtractionPrinter(object):

    def __init__(self,
                 provider: AbstractDocumentProvider,
                 context: int = 50) -> None:
        self.provider = provider
        self.context = context

    def pre_print(self, extraction: Extraction, color: str) -> str:

        filename: str = extraction.document_filename
        start: int = extraction.character_offset - self.context
        end: int = extraction.character_offset + self.context
        text: str = self.provider.get_document_text(filename)
        window: str = "..." + text[start: end] + "..."
        return self._format_for_rich(window, extraction.text_of_extraction, color)

    def _format_for_rich(self,
                         string: str,
                         focal_substring: str,
                         color: str) -> str:
        formatted = f"[bold {color}]{focal_substring}[/bold {color}]"
        return string.replace(focal_substring, formatted)