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
    PRODUCT = "Technical performance and inventory data for products and systems"
    SCENARIO = "Data generated from fore- and nowcasting"
    STATISTICS = "General historical statistical data without links to specific "
    MFA = "Data from MFA (material flow analysis)"
