from enum import StrEnum
from io import BytesIO
from typing import Union

import pandas as pd
import pyarrow as pa
import rfc3987
from peewee import BlobField, TextField
from rdflib import URIRef


class FeatherField(BlobField):
    def db_value(self, value: Union[pd.DataFrame, pa.Table]) -> BytesIO:
        if isinstance(value, pd.DataFrame):
            schema = pa.Schema.from_pandas(value, preserve_index=False)
            table = pa.Table.from_pandas(value, preserve_index=False)
        else:
            schema = value.schema
            table = value

        sink = pa.BufferOutputStream()
        writer = pa.ipc.new_stream(sink, schema)
        writer.write_table(table)
        writer.close()
        return sink.getvalue().to_pybytes()

    def python_value(self, value):
        buffer = pa.py_buffer(value)
        reader = pa.ipc.open_stream(buffer)
        return reader.read_all()


class IRIField(TextField):
    def db_value(self, value: str) -> str:
        if isinstance(value, URIRef):
            value = str(value)
        if not rfc3987.match(value):
            raise ValueError(f"`IRIField` requires a valid IRI; got {value}")
        return value


class DataframeKind(StrEnum):
    # Ideally these would be IRIs in the vocab, and be better informed by standards and provenance
    # Model input parameters and supporting data for executing models. Often measured data or
    # information gathered from technical performance specifications.
    PARAMETERS = "Model input parameters"
    # Broad data about society and economy, including future scenarios. Can include installed
    # capacities or other data which can be used directly for creating virtual markets. Can include
    # prices.
    BROAD = "Broad data about society and economy"
    # Bill of materials to produce a component or assembly. Always in relation to a given output.
    BOM = "Bill of materials, energy, and services"
    # Specific data on composition. Different than model parameters in that these can be
    # individual elements (e.g. for MFA), but are related to a given output (product or economic
    # sector)
    COMPOSITION = "Composition of goods and wastes"
