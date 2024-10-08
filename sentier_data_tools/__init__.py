"""sentier_data_tools."""

__all__ = (
    "__version__",
    "Datapackage",
    "DatapackageWriter" "ProductIRI",
    "Record",
    "UnitIRI",
    "example_data_dir",
    "reset_local_database",
)

__version__ = "0.1.3"

from pathlib import Path

from sentier_data_tools.datapackage import DatapackageWriter
from sentier_data_tools.iri import ProductIRI, UnitIRI
from sentier_data_tools.local_data_store import (
    Datapackage,
    Record,
    db,
    initialize_local_database,
    reset_local_database,
)

initialize_local_database(db)
example_data_dir = Path(__file__).parent.resolve() / "example_data"
