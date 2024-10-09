"""Module for querying RDF triples from sentier.dev vocabularies.

This module provides base classes and utility functions to handle IRIs
and retrieve RDF triples from vocabularies like products and units using SPARQL queries.
"""

from rdflib import Graph, URIRef

from sentier_data_tools.iri.utils import (
    VOCAB_FUSEKI,
    TriplePosition,
    convert_json_object,
    display_value_for_uri,
    execute_sparql_query,
    resolve_hierarchy,
)
from sentier_data_tools.logs import stdout_feedback_logger as logger


class VocabIRI(URIRef):
    """Base class for standard queries for IRIs from sentier.dev vocabularies."""

    def triples(
        self,
        *,
        iri_position: TriplePosition = TriplePosition.SUBJECT,
        limit: int | None = 25,
    ) -> list[tuple]:
        """Get triples from a sentier.dev vocabulary for the given IRI.

        Args:
            iri_position (TriplePosition, optional): The IRI position in the triple
                (SUBJECT, PREDICATE, or OBJECT). Defaults to TriplePosition.SUBJECT.
            limit (int | None, optional): The maximum number of triples to return.
                Defaults to 25.

        Returns:
            list[tuple]: A list of triples from a sentier.dev vocabulary.
        """
        # Ensure a vocabulary graph_url is defined in a subclass
        if not getattr(self, "graph_url", None):
            error_msg = (
                f"{self.__class__.__name__} must define a 'graph_url' attribute "
                "to indicate the vocabulary graph URL."
            )
            logger.error(error_msg)
            raise AttributeError(error_msg)

        # pylint: disable=no-member
        QUERY = f"""
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            
            SELECT ?s ?p ?o
            FROM <{self.graph_url}>
            WHERE {{
                VALUES ?{iri_position.value} {{ <{str(self)}> }}
                ?s ?p ?o
            }}
        """

        if limit is not None:
            QUERY += f"LIMIT {int(limit)}"
        logger.debug(f"Executing query:\n{QUERY}")
        results = execute_sparql_query(QUERY)
        logger.info(f"Retrieved {len(results)} triples from {VOCAB_FUSEKI}")

        return [
            tuple(convert_json_object(line[key]) for key in ["s", "p", "o"])
            for line in results
        ]

    def __repr__(self) -> str:
        return self.display()

    def display(self) -> str:
        return display_value_for_uri(str(self), self.kind, self.graph_url)

    def graph(
        self,
        *,
        iri_position: TriplePosition = TriplePosition.SUBJECT,
    ) -> Graph:
        """Return an `rdflib` graph of the data from the sentier.dev vocabulary for this IRI."""
        graph = Graph()
        for triple in self.triples(
            iri_position=iri_position,
            limit=None,
        ):
            graph.add(triple)
        return graph

    def narrower(
        self, include_self: bool = False, raw_strings: bool = False
    ) -> list["VocabIRI"] | list[str]:
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
    ) -> list["VocabIRI"] | list[str]:
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
