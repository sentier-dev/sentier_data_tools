from io import BytesIO
from pathlib import Path
from typing import Union

import pandas as pd
import platformdirs
import pyarrow as pa
from peewee import BlobField, ForeignKeyField, IntegerField, Model, TextField, fn
from playhouse.sqlite_ext import JSONField, SqliteExtDatabase

base_dir = Path(platformdirs.user_data_dir(appname="sentier.dev", appauthor="DdS"))
sqlite_dir_platformdirs = base_dir / "local-data-store"
sqlite_dir_platformdirs.mkdir(exist_ok=True, parents=True)

DB_NAME = "datapackages.db"
db = SqliteExtDatabase(sqlite_dir_platformdirs / DB_NAME)


def initialize_local_database(db: SqliteExtDatabase):
    """Initialize the database, creating tables if they do not exist."""
    db.connect(reuse_if_open=True)
    db.create_tables([Record, Datapackage], safe=True)
    db.close()


def reset_local_database():
    """Initialize the database, creating tables if they do not exist."""
    Record.delete().execute()
    Datapackage.delete().execute()


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


class Datapackage(Model):
    name = TextField()
    metadata = JSONField()
    version = IntegerField()

    class Meta:
        database = db


class Record(Model):
    data = FeatherField()
    product = TextField()
    columns = JSONField()
    units = JSONField()
    datapackage = ForeignKeyField(Datapackage, backref="records")

    class Meta:
        database = db


# Function to query records by a column name
def query_records_by_column(column_value):
    """Returns a list of records where the specified column is present."""
    query = Record.select().where(
        fn.JSON_CONTAINS(Record.columns, f'["{column_value}"]')
    )
    return list(query)
