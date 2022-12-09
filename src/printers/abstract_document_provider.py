from abc import ABC, abstractmethod


class AbstractDocumentProvider(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_document_text(self, doc_identifier: str) -> str:
        pass
