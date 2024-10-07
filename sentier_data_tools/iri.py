from rdflib import Graph, Literal, URIRef
from SPARQLWrapper import JSON, SPARQLWrapper

from sentier_data_tools.logs import stdout_feedback_logger as logger
from sentier_data_tools.utils import TriplePosition

VOCAB_FUSEKI = "https://fuseki.d-d-s.ch/skosmos/query"


def convert_json_object(obj: dict) -> URIRef | Literal:
    """Convert a JSON-formatted SPARQL Query Result object into an rdflib URIRef or Literal."""
    if obj["type"] == "literal":
        return Literal(
            obj["value"], lang=obj.get("xml:lang"), datatype=obj.get("datatype")
        )
    elif obj["type"] == "uri":
        return URIRef(obj["value"])
    else:
        error_msg = f"Unknown object type {obj['type']}"
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
            iri_position (TriplePosition, optional): The position of the IRI in the triple.
                Can be SUBJECT, PREDICATE, or OBJECT. Defaults to TriplePosition.SUBJECT.
            limit (int | None, optional): The maximum number of triples to return. Defaults to 25.

        Returns:
            list[tuple]: A list of triples from a sentier.dev vocabulary.
        """
        # Ensure a vocabulary graph_url is defined in the subclass
        if not getattr(self, "graph_url", None):
            error_msg = f"{self.__class__.__name__}, must define a class-level 'graph_url' attribute to indicate the vocabulary graph URL."
            logger.error(error_msg)
            raise AttributeError(error_msg)

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
        logger.debug(f"Executing query:\n{query}")
        results = sparql.queryAndConvert()["results"]["bindings"]
        logger.info(f"Retrieved {len(results)} triples from {VOCAB_FUSEKI}")

        return [
            tuple(convert_json_object(line[key]) for key in ["s", "p", "o"])
            for line in results
        ]

    def graph(self, *, iri_position: TriplePosition = TriplePosition.SUBJECT) -> Graph:
        """Return an `rdflib` graph of the data from the sentier.dev vocabulary for this IRI."""
        graph = Graph()
        for triple in self.triples(iri_position=iri_position, limit=None):
            graph.add(triple)
        return graph


class ProductIRI(VocabIRI):
    """Class for standard queries for IRIs from the products vocabulary."""

    graph_url = "https://vocab.sentier.dev/products/"


class UnitIRI(VocabIRI):
    """Class for standard queries for IRIs from the units vocabulary."""

    graph_url = "https://vocab.sentier.dev/qudt/"
