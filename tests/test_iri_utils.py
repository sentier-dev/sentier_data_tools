"""Unit tests for IRI classes and their helper functions.

These tests focus on verifying the core functionality of the VocabIRI class and its
subclasses (ProductIRI and UnitIRI). The primary behavior of ProductIRI and UnitIRI,
such as SPARQL querying and triple retrieval, should be covered in integration tests.
"""

from unittest.mock import patch

import pytest
from rdflib import Literal, URIRef

from sentier_data_tools.iri import (
    ProductIRI,
    SPARQLWrapper,
    VocabIRI,
    convert_json_object,
)
from sentier_data_tools.utils import TriplePosition


# Test convert_json_object function
def test_convert_json_object_literal() -> None:
    obj = {
        "type": "literal",
        "value": "Hello World",
        "xml:lang": "en",
    }
    result = convert_json_object(obj)
    assert isinstance(result, Literal)
    assert result.value == "Hello World"
    assert result.language == "en"


def test_convert_json_object_uri() -> None:
    obj = {
        "type": "uri",
        "value": "https://example.com",
    }
    result = convert_json_object(obj)
    assert isinstance(result, URIRef)
    assert str(result) == "https://example.com"


def test_convert_json_object_missing_type() -> None:
    obj = {"value": "Missing type"}
    with pytest.raises(ValueError, match="Missing 'type' key in object:"):
        convert_json_object(obj)


def test_convert_json_object_unknown_type() -> None:
    obj = {"type": "unknown", "value": "Unknown type"}
    with pytest.raises(ValueError, match="Unknown object type 'unknown'"):
        convert_json_object(obj)


# Test Vocab IRI class without get_url attribute
class IncompleteVocabIRI(VocabIRI):
    """Subclass of VocabIRI without graph_url to test the get_url error."""


@pytest.fixture
def incomplete_vocab_iri() -> IncompleteVocabIRI:
    return IncompleteVocabIRI("https://example.org/incomplete/123")


def test_vocab_iri_missing_graph_url(
    incomplete_vocab_iri: IncompleteVocabIRI,
) -> None:
    """Test that AttributeError is raised when graph_url is missing."""
    with pytest.raises(AttributeError, match="must define a 'graph_url' attribute"):
        incomplete_vocab_iri.triples()


# Test base functionality of ProductIRI for each TriplePosition value


@pytest.fixture
def product_iri() -> ProductIRI:
    return ProductIRI("https://example.com/product/123")


# Helper function to mock SPARQLWrapper results
def mock_sparql_result(mock_sparql, iri_value, position):
    # Default values for s, p, o
    default_values = {
        "s": {"type": "uri", "value": "https://example.com/default_subject"},
        "p": {"type": "uri", "value": "https://example.com/default_predicate"},
        "o": {"type": "literal", "value": "default_object"},
    }

    # Overwrite the default value for the corresponding TriplePosition
    if position == TriplePosition.SUBJECT:
        default_values["s"] = {"type": "uri", "value": iri_value}
    elif position == TriplePosition.PREDICATE:
        default_values["p"] = {"type": "uri", "value": iri_value}
    elif position == TriplePosition.OBJECT:
        default_values["o"] = {"type": "literal", "value": iri_value}

    mock_sparql_instance = mock_sparql.return_value
    mock_sparql_instance.queryAndConvert.return_value = {
        "results": {"bindings": [default_values]}
    }


@pytest.mark.parametrize(
    "position",
    [TriplePosition.SUBJECT, TriplePosition.PREDICATE, TriplePosition.OBJECT],
)
@patch("sentier_data_tools.iri.SPARQLWrapper")
def test_product_iri_triples_for_all_positions(
    mock_sparql: SPARQLWrapper, product_iri: ProductIRI, position: TriplePosition
) -> None:
    """Test that ProductIRI works for all values of TriplePosition."""
    mock_sparql_result(mock_sparql, "https://example.com/product/123", position)

    triples = product_iri.triples(iri_position=position)

    assert len(triples) == 1
    if position == TriplePosition.SUBJECT:
        assert isinstance(triples[0][0], URIRef)
        assert str(triples[0][0]) == "https://example.com/product/123"
    elif position == TriplePosition.PREDICATE:
        assert isinstance(triples[0][1], URIRef)
        assert str(triples[0][1]) == "https://example.com/product/123"
    elif position == TriplePosition.OBJECT:
        assert isinstance(triples[0][2], Literal)
        assert str(triples[0][2]) == "https://example.com/product/123"
