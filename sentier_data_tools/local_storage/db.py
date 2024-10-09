from pathlib import Path

import platformdirs
from peewee import DateField, IntegerField, Model, TextField
from peewee_enum_field import EnumField
from playhouse.sqlite_ext import JSONField, SqliteExtDatabase

from sentier_data_tools.local_storage.fields import (
    ColumnsField,
    DatasetKind,
    GeonamesIRIField,
    PandasFeatherField,
    ProductIRIField,
)

base_dir = Path(platformdirs.user_data_dir(appname="sentier.dev", appauthor="DdS"))
sqlite_dir_platformdirs = base_dir / "local-data-store"
sqlite_dir_platformdirs.mkdir(exist_ok=True, parents=True)

DB_NAME = "datasets.db"
sqlite_db = SqliteExtDatabase(sqlite_dir_platformdirs / DB_NAME)


def initialize_local_database(db: SqliteExtDatabase) -> None:
    """Initialize the database, creating tables if they do not exist."""
    db.connect(reuse_if_open=True)
    db.create_tables([Dataset], safe=True)
    db.close()


def global_location_default() -> str:
    return "https://sws.geonames.org/6295630/"


def reset_local_database() -> None:
    """Initialize the database, creating tables if they do not exist."""
    Dataset.delete().execute()


class Dataset(Model):
    name = TextField()
    dataframe = PandasFeatherField()
    kind = EnumField(DatasetKind, default=DatasetKind.PARAMETERS)
    product = ProductIRIField(null=True)
    location = GeonamesIRIField(default=global_location_default)
    valid_from = DateField()
    valid_to = DateField()
    columns = ColumnsField()
    metadata = JSONField()
    version = IntegerField()

    # TODO: BOM must have "determining_value" column in metadata

    class Meta:
        database = sqlite_db
