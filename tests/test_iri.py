import pytest
from rdflib import Literal, URIRef

from sentier_data_tools.iri import convert_json_object


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
