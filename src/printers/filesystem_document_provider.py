from src.printers.abstract_document_provider import AbstractDocumentProvider


class FilesystemDocumentProvider(AbstractDocumentProvider):

    def get_document_text(self, doc_identifier: str) -> str:
        with open(doc_identifier, "r") as inf:
            return inf.read()