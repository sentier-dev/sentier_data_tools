from typing import List, Optional, Union

from rdflib import Graph, URIRef

from sentier_data_tools.iri.utils import (
    VOCAB_FUSEKI,
    convert_json_object,
    display_value_for_uri,
    execute_sparql_query,
    resolve_hierarchy,
)
from sentier_data_tools.logs import stdout_feedback_logger as logger


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

    def __repr__(self) -> str:
        return self.display()

    def display(self) -> str:
        return display_value_for_uri(str(self), self.kind, self.graph_url)

    def graph(self, subject: bool = True) -> Graph:
        """Return an `rdflib` graph of the data from the sentier.dev vocabulary for this IRI"""
        graph = Graph()
        for triple in self.triples(subject=subject, limit=None):
            graph.add(triple)
        return graph

    def narrower(
        self, include_self: bool = False, raw_strings: bool = False
    ) -> Union[list["VocabIRI"], list[str]]:
        QUERY = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?o ?s
FROM <{self.graph_url}>
WHERE {{
    <{str(self)}> skos:narrower+ ?o .
    ?o skos:broader ?s .
}}"""
        logger.debug(f"Executing query:\n{QUERY}")
        results = [
            (elem["s"]["value"], elem["o"]["value"])
            for elem in execute_sparql_query(QUERY)
        ]
        logger.info(f"Retrieved {len(results)} triples from {VOCAB_FUSEKI}")
        ordered = resolve_hierarchy(results, str(self), include_self)

        if raw_strings:
            return ordered
        else:
            return [self.__class__(elem) for elem in ordered]

    def broader(
        self, include_self: bool = False, raw_strings: bool = False
    ) -> Union[list["VocabIRI"], list[str]]:
        QUERY = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?o ?s
FROM <{self.graph_url}>
WHERE {{
    <{str(self)}> skos:broader+ ?o .
    ?o skos:narrower ?s .
}}"""
        logger.debug(f"Executing query:\n{QUERY}")
        results = [
            (elem["s"]["value"], elem["o"]["value"])
            for elem in execute_sparql_query(QUERY)
        ]
        logger.info(f"Retrieved {len(results)} triples from {VOCAB_FUSEKI}")
        ordered = resolve_hierarchy(results, str(self), include_self)

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

    def narrower(self, include_self: bool = False, raw_strings: bool = False) -> list:
        # Model terms are not arranged in a hierarchy
        if include_self and raw_strings:
            return [str(self)]
        elif include_self:
            return [self]
        else:
            return []

    def broader(self, *args, **kwargs):
        return self.narrower(*args, **kwargs)


class FlowIRI(VocabIRI):
    kind = "flow"
    graph_url = "https://vocab.sentier.dev/flows/"


class GeonamesIRI(URIRef):
    pass
