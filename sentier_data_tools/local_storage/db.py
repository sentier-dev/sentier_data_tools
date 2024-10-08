from pathlib import Path

import platformdirs
from peewee import DateField, IntegerField, Model, TextField
from peewee_enum_field import EnumField
from playhouse.sqlite_ext import JSONField, SqliteExtDatabase

from sentier_data_tools.local_storage.fields import (
    DataframeKind,
    FeatherField,
    IRIField,
)

base_dir = Path(platformdirs.user_data_dir(appname="sentier.dev", appauthor="DdS"))
sqlite_dir_platformdirs = base_dir / "local-data-store"
sqlite_dir_platformdirs.mkdir(exist_ok=True, parents=True)

DB_NAME = "dataframe.db"
sqlite_db = SqliteExtDatabase(sqlite_dir_platformdirs / DB_NAME)


def initialize_local_database(db: SqliteExtDatabase):
    """Initialize the database, creating tables if they do not exist."""
    db.connect(reuse_if_open=True)
    db.create_tables([Dataframe], safe=True)
    db.close()


def global_location_default():
    return "https://sws.geonames.org/6295630/"


def reset_local_database():
    """Initialize the database, creating tables if they do not exist."""
    Dataframe.delete().execute()


class Dataframe(Model):
    name = TextField()
    data = FeatherField()
    kind = EnumField(DataframeKind, default=DataframeKind.PRODUCT)
    product = IRIField(null=True)
    location = IRIField(default=global_location_default)
    valid_from = DateField()
    valid_to = DateField()
    columns = JSONField()  # Includes units
    metadata = JSONField()
    version = IntegerField()

    class Meta:
        database = sqlite_db

    @property
    def dataframe(self):
        return self.data.to_pandas()
