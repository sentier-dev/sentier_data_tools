from functools import lru_cache
from typing import List, Optional

from sentier_data_tools.iri import UnitIRI
from sentier_data_tools.iri.utils import execute_sparql_query
from sentier_data_tools.logs import stdout_feedback_logger as logger

UNITS_GRAPH = "https://vocab.sentier.dev/units/"


@lru_cache(maxsize=512)
def get_units_for_quantity_kind(qk: str) -> list:
    QUERY = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX qudt: <http://qudt.org/schema/qudt/>

SELECT ?unit ?conversion
FROM <{UNITS_GRAPH}>
WHERE {{
    ?unit qudt:hasQuantityKind <{qk}> .
    ?unit a skos:Concept .
    <{qk}> skos:narrowerTransitive ?unit .
    ?unit a skos:Concept .
    ?unit qudt:conversionMultiplier ?conversion .
}}
        """
    logger.debug("Executing query %s", QUERY)
    result = execute_sparql_query(QUERY)
    if not result:
        raise KeyError(f"IRI `{qk}` not in units graph")
    return {
        line["unit"]["value"]: float(line["conversion"]["value"]) for line in result
    }


@lru_cache(maxsize=512)
def get_quantity_kinds_for_unit(iri: UnitIRI) -> str:
    QUERY = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX qudt: <http://qudt.org/schema/qudt/>

SELECT ?quantitykind
FROM <{UNITS_GRAPH}>
WHERE {{
    ?quantitykind skos:inScheme <{UNITS_GRAPH}> .
    <{iri}> qudt:hasQuantityKind ?quantitykind
}}
        """
    logger.debug("Executing query %s", QUERY)
    result = execute_sparql_query(QUERY)
    if not result:
        raise KeyError(f"IRI `{iri}` not in units graph")
    return {line["quantitykind"]["value"] for line in result}


@lru_cache(maxsize=2048)
def get_conversion_factor(from_iri: UnitIRI, to_iri: UnitIRI) -> float:
    qk1 = get_quantity_kinds_for_unit(from_iri)
    qk2 = get_quantity_kinds_for_unit(to_iri)
    common = qk1.intersection(qk2)
    if not common:
        raise ValueError("Given units have no common quantity kinds")
    logger.debug(
        "Found common quantity keys for %s to %s: %s", from_iri, to_iri, common
    )
    conversion_dict = {}
    for qk in common:
        conversion_dict.update(get_units_for_quantity_kind(qk))

    return conversion_dict[str(from_iri)] / conversion_dict[str(to_iri)]
