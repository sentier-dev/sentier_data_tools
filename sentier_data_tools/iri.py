from typing import List, Optional, Union
from rdflib import URIRef, Literal, Graph

from SPARQLWrapper import JSON, SPARQLWrapper

from sentier_data_tools.logs import stdout_feedback_logger as logger

VOCAB_FUSEKI = "https://fuseki.d-d-s.ch/skosmos/query"


def convert_json_object(obj: dict) -> Union[URIRef, Literal]:
    if obj['type'] == 'literal':
        return Literal(obj['value'], lang=obj.get("xml:lang"), datatype=obj.get('datatype'))
    else:
        return URIRef(obj['value'])


class VocabIRI(URIRef):
    def triples(self, *, subject: bool = True, limit: Optional[int] = 25) -> List[tuple]:
        """Return a list of triples with `rdflib` objects"""
        if subject:
            QUERY = f"""
                SELECT ?s ?p ?o
                FROM <{self.graph_url}>
                WHERE {{
                    VALUES ?s {{ <{str(self)}> }}
                    ?s ?p ?o
                }}
            """
            
        else:
            QUERY = f"""
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                SELECT ?s ?p ?o
                FROM <{self.graph_url}>
                WHERE {{
                    VALUES ?o {{ <{str(self)}> }}
                    ?s ?p ?o
                }}
            """
        if limit is not None:
            QUERY += f"LIMIT {int(limit)}"
        sparql = SPARQLWrapper(VOCAB_FUSEKI)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(QUERY)
        logger.debug(f"Executing query:\n{QUERY}")
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
