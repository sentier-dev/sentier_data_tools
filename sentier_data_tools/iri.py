import locale
import platform
from collections import deque, defaultdict
from functools import lru_cache
from itertools import groupby
from typing import List, Optional, Union

from rdflib import Graph, Literal, URIRef
from SPARQLWrapper import JSON, SPARQLWrapper

from sentier_data_tools.logs import stdout_feedback_logger as logger

if platform.system() == "Windows":
    import ctypes

    windll = ctypes.windll.kernel32
    windll.GetUserDefaultUILanguage()
    language = locale.windows_locale[windll.GetUserDefaultUILanguage()]
else:
    language = locale.getlocale()[0]

VOCAB_FUSEKI = "https://fuseki.d-d-s.ch/skosmos/query"


sparql = SPARQLWrapper(VOCAB_FUSEKI)
sparql.setReturnFormat(JSON)


def execute_sparql_query(query: str) -> list:
    sparql.setQuery(query)
    return sparql.queryAndConvert()["results"]["bindings"]


def convert_json_object(obj: dict) -> Union[URIRef, Literal]:
    if obj["type"] == "literal":
        return Literal(
            obj["value"], lang=obj.get("xml:lang"), datatype=obj.get("datatype")
        )
    else:
        return URIRef(obj["value"])


class VocabIRI(URIRef):
    def triples(self, subject: bool = True, limit: Optional[int] = 25) -> List[tuple]:
        """Return a list of triples with `rdflib` objects"""
        if subject:
            QUERY = f"""
    SELECT ?p ?o
    FROM <{self.graph_url}>
    WHERE {{
        <{str(self)}> ?p ?o
    }}
            """
        else:
            QUERY = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT ?s ?p
    FROM <{self.graph_url}>
    WHERE {{
        ?s ?p <{str(self)}>
    }}
            """
        if limit is not None:
            QUERY += f"LIMIT {int(limit)}"
        logger.debug(f"Executing query:\n{QUERY}")
        results = execute_sparql_query(QUERY)
        logger.info(f"Retrieved {len(results)} triples from {VOCAB_FUSEKI}")

        if subject:
            return [
                (
                    URIRef(str(self)),
                    convert_json_object(line["p"]),
                    convert_json_object(line["o"]),
                )
                for line in results
            ]
        else:
            return [
                (
                    convert_json_object(line["s"]),
                    convert_json_object(line["p"]),
                    URIRef(str(self)),
                )
                for line in results
            ]

    def display(self) -> str:
        return display_value_for_uri(str(self), self.kind, self.graph_url)

    def graph(self, subject: bool = True) -> Graph:
        """Return an `rdflib` graph of the data from the sentier.dev vocabulary for this IRI"""
        graph = Graph()
        for triple in self.triples(subject=subject, limit=None):
            graph.add(triple)
        return graph

    def narrower(self, include_self: bool = False, raw_strings: bool = False) -> list["VocabIRI"]:
        QUERY = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?o ?s
FROM <{self.graph_url}>
WHERE {{
    <{str(self)}> skos:narrower+ ?o .
    ?o skos:broader ?s .
}}"""
        logger.debug(f"Executing query:\n{QUERY}")
        results = [(elem['s']['value'], elem['o']['value']) for elem in execute_sparql_query(QUERY)]
        logger.info(f"Retrieved {len(results)} triples from {VOCAB_FUSEKI}")

        ordered, queue, grouped = [], deque([str(self)]), defaultdict(list)
        for s, o in results:
            grouped[s].append(o)

        if include_self:
            ordered.append(str(self))

        while queue:
            current = queue.popleft()
            if current in grouped:
                for code in grouped[current]:
                    if code in ordered:
                        continue
                    ordered.append(URIRef(code))
                    if code in grouped:
                        queue.append(code)

        if raw_strings:
            return ordered
        else:
            return [self.__class__(elem) for elem in ordered]


class ProductIRI(VocabIRI):
    kind = "product"
    graph_url = "https://vocab.sentier.dev/products/"


class UnitIRI(VocabIRI):
    kind = "unit"
    graph_url = "https://vocab.sentier.dev/units/"


class ModelTermIRI(VocabIRI):
    kind = "model-term"
    graph_url = "https://vocab.sentier.dev/model-terms/"


class FlowIRI(VocabIRI):
    kind = "flow"
    graph_url = "https://vocab.sentier.dev/flows/"


class GeonamesIRI(URIRef):
    pass


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
