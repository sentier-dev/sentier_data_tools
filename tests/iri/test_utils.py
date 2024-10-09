import pytest
from rdflib import Literal, URIRef

from sentier_data_tools.iri.utils import convert_json_object


def test_convert_json_object_literal_with_language() -> None:
    """Test that a literal object is correctly converted."""
    obj = {
        "type": "literal",
        "value": "Hello World",
        "xml:lang": "en",
    }
    result = convert_json_object(obj)
    assert isinstance(result, Literal)
    assert result.value == "Hello World"
    assert result.language == "en"
    assert result.datatype is None


def test_convert_json_object_literal_with_datatype() -> None:
    """Test that a literal object with a datatype is correctly converted."""
    obj = {
        "type": "literal",
        "value": "42",
        "datatype": "http://www.w3.org/2001/XMLSchema#int",
    }
    result = convert_json_object(obj)
    print(result)
    assert isinstance(result, Literal)
    assert result.value == 42
    assert result.datatype == URIRef("http://www.w3.org/2001/XMLSchema#int")


def test_convert_json_object_uri() -> None:
    """Test that a URI object is correctly converted to URIRef."""
    obj = {
        "type": "uri",
        "value": "https://example.com",
    }
    result = convert_json_object(obj)
    assert isinstance(result, URIRef)
    assert str(result) == "https://example.com"


def test_convert_json_object_missing_value_key() -> None:
    """Test that a ValueError is raised when the 'value' key is missing."""
    obj = {
        "type": "literal",
    }
    with pytest.raises(ValueError, match="Missing 'value' key in object:"):
        convert_json_object(obj)


def test_convert_json_object_unknown_type() -> None:
    """Test that a non-literal and non-uri type returns URIRef (default behavior)."""
    obj = {
        "type": "unknown",
        "value": "https://example.com/unknown",
    }
    result = convert_json_object(obj)
    assert isinstance(result, URIRef)
    assert str(result) == "https://example.com/unknown"
