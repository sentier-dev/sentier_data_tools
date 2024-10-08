"""Module for querying RDF triples from sentier.dev vocabularies.

This module provides base classes and utility functions to handle IRIs
and retrieve RDF triples from vocabularies like products and units using SPARQL queries.
"""

from rdflib import Graph, Literal, URIRef
from SPARQLWrapper import JSON, SPARQLWrapper

from sentier_data_tools.logs import stdout_feedback_logger as logger
from sentier_data_tools.utils import TriplePosition

VOCAB_FUSEKI = "https://fuseki.d-d-s.ch/skosmos/query"


def convert_json_object(
    obj: dict,
) -> URIRef | Literal:
    """Convert a SPARQL result object to rdflib URIRef or Literal."""
    obj_type = obj.get("type")

    if obj_type == "literal":
        return Literal(
            obj["value"],
            lang=obj.get("xml:lang"),
            datatype=obj.get("datatype"),
        )
    if obj_type == "uri":
        return URIRef(obj["value"])

    if obj_type is None:
        error_msg = f"Missing 'type' key in object: {obj}."
    else:
        error_msg = f"Unknown object type '{obj_type}' in object: {obj}"

    logger.error(error_msg)
    raise ValueError(error_msg)


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
        query = f"""
            SELECT ?s ?p ?o
            FROM <{self.graph_url}>
            WHERE {{
                VALUES ?{iri_position.value} {{ <{str(self)}> }}
                ?s ?p ?o
            }}
        """

        if limit is not None:
            query += f"LIMIT {int(limit)}"
        sparql = SPARQLWrapper(VOCAB_FUSEKI)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        logger.debug("Executing query:\n%s", query)
        results = sparql.queryAndConvert()["results"]["bindings"]
        logger.info("Retrieved %d triples from %s", len(results), VOCAB_FUSEKI)

        return [
            tuple(convert_json_object(line[key]) for key in ["s", "p", "o"])
            for line in results
        ]

    def graph(
        self,
        *,
        iri_position: TriplePosition = TriplePosition.SUBJECT,
    ) -> Graph:
        """Return a graph of the triples for this IRI."""
        graph = Graph()
        for triple in self.triples(
            iri_position=iri_position,
            limit=None,
        ):
            graph.add(triple)
        return graph


class ProductIRI(VocabIRI):
    """Standard queries for IRIs from the Products vocabulary."""

    graph_url = "https://vocab.sentier.dev/products/"


class UnitIRI(VocabIRI):
    """Standard queries for IRIs from the Units vocabulary."""

    graph_url = "https://vocab.sentier.dev/units/"


class ModelTermIRI(VocabIRI):
    """Standard queries for IRIs from the Model Terms vocabulary."""

    graph_url = "https://vocab.sentier.dev/model-terms/"


class GeonamesIRI(URIRef):
    """Standard queries for IRIs from the external GeoNames vocabulary."""

    graph_url = "https://www.geonames.org/"
