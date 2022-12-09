from typing import Tuple

from spacy.tokens import Doc, Span


class MatchUnpacker(object):
    def match2variables(
        self, match_kind: str, match_span: Span
    ) -> Tuple[Span, Span]:
        """
        Some of the matches have X and Y variables

        This method returns the X and Y variables
        """
        if match_kind.startswith("effect_of_x_on_y"):
            # e.g. 'effect of rainfall on remittences'
            on_index = next(
                ino
                for ino, i in enumerate(match_span)
                if str(i).lower() == "on"
            )
            start_of_NP_index = 2  # 2 for "effect on"
            variable_x = match_span[start_of_NP_index:on_index]
            word_after_on_index = on_index + 1
            variable_y = match_span[word_after_on_index:]
            return (variable_x, variable_y)
        if match_kind.startswith("positive_effect_on"):
            on_index = next(
                ino
                for ino, i in enumerate(match_span)
                if str(i).lower() == "on"
            )
            to_index = next(
                ino
                for ino, i in enumerate(match_span)
                if str(i).lower() == "to"
            )
            word_after_on_index = on_index + 1
            variable_y = match_span[word_after_on_index:]
            variable_x = match_span[0:to_index]
            return (variable_x, variable_y)
        if match_kind.startswith("relationship_between"):
            # e.g. 'effect of rainfall on remittences'
            on_index = next(
                ino
                for ino, i in enumerate(match_span)
                if str(i).lower() == "and"
            )
            start_of_NP_index = 2  # 2 for "relationship between"
            variable_x = match_span[start_of_NP_index:on_index]
            word_after_on_index = on_index + 1
            variable_y = match_span[word_after_on_index:]
            return (variable_x, variable_y)
        if match_kind.startswith("NP_"):
            variable_x = match_span
            return (variable_x, variable_x)
