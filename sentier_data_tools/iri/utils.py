import locale
import os
import platform
from collections import defaultdict, deque
from enum import Enum
from functools import lru_cache
from typing import Union

from rdflib import Literal, URIRef
from SPARQLWrapper import JSON, SPARQLWrapper

from sentier_data_tools.logs import stdout_feedback_logger as logger

if language := os.environ.get("SDT_LOCALE"):
    pass
elif platform.system() == "Windows":
    import ctypes

    windll = ctypes.windll.kernel32
    windll.GetUserDefaultUILanguage()
    language = locale.windows_locale[windll.GetUserDefaultUILanguage()] or "en"
else:
    language = locale.getlocale()[0] or "en"  # Sigh...

VOCAB_FUSEKI = "https://fuseki.d-d-s.ch/skosmos/query"


sparql = SPARQLWrapper(VOCAB_FUSEKI)
sparql.setReturnFormat(JSON)


def execute_sparql_query(query: str) -> list:
    sparql.setQuery(query)
    return sparql.queryAndConvert()["results"]["bindings"]


def convert_json_object(obj: dict) -> URIRef | Literal:
    if "value" not in obj:
        error_msg = f"Missing 'value' key in object: {obj}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if obj["type"] == "literal":
        return Literal(
            obj["value"], lang=obj.get("xml:lang"), datatype=obj.get("datatype")
        )
    else:
        return URIRef(str(obj["value"]))


@lru_cache(maxsize=2048)
def display_value_for_uri(
    iri: str,
    kind: str,
    graph_url: str,
    language: str = language,
    fallback_language: str = "en",
) -> str:
    QUERY = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?label
FROM <{graph_url}>
WHERE {{
<{iri}> skos:prefLabel ?label .
FILTER (strstarts(lang(?label), '{language.lower()[:2]}'))
}}"""
    results = execute_sparql_query(QUERY)

    if not results:
        QUERY = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT ?label
    FROM <{graph_url}>
    WHERE {{
    <{iri}> skos:prefLabel ?label .
    FILTER (strstarts(lang(?label), '{fallback_language.lower()[:2]}'))
    }}"""
        results = execute_sparql_query(QUERY)

    if results:
        return f"<{iri}>: {results[0]['label']['value']} ({kind})"
    else:
        return f"<{iri}>: Missing label ({kind})"


def resolve_hierarchy(
    data: list[tuple[str, str]], start: str, include_start: bool
) -> list[str]:
    """Give a list of `(parent, child)` tuples, create a list of children in breadth-first order"""
    ordered, queue, grouped = [], deque([start]), defaultdict(list)
    for s, o in data:
        grouped[s].append(o)

    if include_start:
        ordered.append(start)

    while queue:
        current = queue.popleft()
        if current in grouped:
            for code in grouped[current]:
                if code in ordered:
                    continue
                ordered.append(code)
                if code in grouped:
                    queue.append(code)

    return ordered


class TriplePosition(Enum):
    """Represents the position of an object in a triple store."""

    SUBJECT = "s"
    PREDICATE = "p"
    OBJECT = "o"
