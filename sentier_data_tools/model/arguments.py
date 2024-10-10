from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

# from sentier_data_tools.data_source_base import DataSourceBase
from sentier_data_tools.iri import FlowIRI, GeonamesIRI, ProductIRI, UnitIRI

# from sentier_data_tools.local_storage import DefaultDataSource


class Edge(BaseModel):
    unit_iri: UnitIRI
    amount: float
    spatial_context: GeonamesIRI = GeonamesIRI("https://sws.geonames.org/6295630/")
    properties: Optional[list] = None
    begin_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Demand(Edge):
    product_iri: ProductIRI


class Flow(Edge):
    flow_iri: FlowIRI

    model_config = ConfigDict(arbitrary_types_allowed=True)


class RunConfig(BaseModel):
    num_samples: int = 1000
    # data_source: Optional[DataSourceBase] = DefaultDataSource

    model_config = ConfigDict(arbitrary_types_allowed=True)
