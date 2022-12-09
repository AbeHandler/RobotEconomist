from dataclasses import dataclass


@dataclass
class Extraction:
    '''Something extracted from a document'''
    kind_of_extraction: str   # e.g. IV or outcome or effects
    text_of_extraction: str   # e.g.  "slope of terrain"
    document_filename: str
    character_offset: int
    # if add more fields be sure to adjust eq

    def __eq__(self, other) -> bool:  # type: ignore
        if not self.kind_of_extraction == other.kind_of_extraction:
            return False
        if not self.text_of_extraction == other.text_of_extraction:
            return False
        if not self.document_filename == other.document_filename:
            return False
        if not self.character_offset == other.character_offset:
            return False
        return True
