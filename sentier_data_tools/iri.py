from rdflib import URIRef, Literal, Graph

from SPARQLWrapper import JSON, SPARQLWrapper

from sentier_data_tools.logs import stdout_feedback_logger as logger

VOCAB_FUSEKI = "https://fuseki.d-d-s.ch/skosmos/query"


def convert_json_object(obj: dict) -> URIRef | Literal:
    if obj['type'] == 'literal':
        return Literal(obj['value'], lang=obj.get("xml:lang"), datatype=obj.get('datatype'))
    elif obj['type'] == 'uri':
        return URIRef(obj['value'])
    else:
        error_msg = f"Unknown object type {obj['type']}"
        logger.error(error_msg)
        raise ValueError(error_msg)


class VocabIRI(URIRef):
    def triples(self, *, subject: bool = True, limit: int | None = 25) -> list[tuple]:
        """Return a list of triples with `rdflib` objects"""
        if subject:
            query = f"""
                SELECT ?s ?p ?o
                FROM <{self.graph_url}>
                WHERE {{
                    VALUES ?s {{ <{str(self)}> }}
                    ?s ?p ?o
                }}
            """
            
        else:
            query = f"""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                SELECT ?s ?p ?o
                FROM <{self.graph_url}>
                WHERE {{
                    VALUES ?o {{ <{str(self)}> }}
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
            (
                convert_json_object(line['s']),
                convert_json_object(line['p']),
                convert_json_object(line['o'])
            )
            for line in results
        ]

    def graph(self, *, subject: bool = True) -> Graph:
        """Return an `rdflib` graph of the data from the sentier.dev vocabulary for this IRI"""
        graph = Graph()
        for triple in self.triples(subject=subject, limit=None):
            graph.add(triple)
        return graph


class ProductIRI(VocabIRI):
    graph_url = "https://vocab.sentier.dev/products/"


class UnitIRI(VocabIRI):
    graph_url = "https://vocab.sentier.dev/qudt/"
