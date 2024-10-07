"""Unit tests for IRI classes and their helper functions.

These tests focus on verifying the core functionality of the VocabIRI class and its
subclasses (ProductIRI and UnitIRI). The primary behavior of ProductIRI and UnitIRI,
such as SPARQL querying and triple retrieval, should be covered in integration tests.
"""

import pytest
from rdflib import Literal, URIRef

from sentier_data_tools.iri import VocabIRI, convert_json_object


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
def incomplete_vocab_iri_class() -> IncompleteVocabIRI:
    return IncompleteVocabIRI("https://example.org/incomplete/123")


def test_vocab_iri_missing_graph_url(
    incomplete_vocab_iri_class: IncompleteVocabIRI,
) -> None:
    """Test that AttributeError is raised when graph_url is missing."""
    with pytest.raises(AttributeError, match="must define a 'graph_url' attribute"):
        incomplete_vocab_iri_class.triples()
