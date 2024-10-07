from enum import Enum


class TriplePosition(Enum):
    """Represents the position of an object in a triple store."""

    SUBJECT = "s"
    PREDICATE = "p"
    OBJECT = "o"
