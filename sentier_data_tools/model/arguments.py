from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

# from sentier_data_tools.data_source_base import DataSourceBase
from sentier_data_tools.iri import FlowIRI, GeonamesIRI, ProductIRI

# from sentier_data_tools.local_storage import DefaultDataSource


class Demand(BaseModel):
    product_iri: ProductIRI
    properties: Optional[list]
    amount: float
    spatial_context: GeonamesIRI = GeonamesIRI("https://sws.geonames.org/6295630/")
    begin_date: Optional[date] = None
    end_date: Optional[date] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Flow(BaseModel):
    flow_iri: FlowIRI

    model_config = ConfigDict(arbitrary_types_allowed=True)


class RunConfig(BaseModel):
    num_samples: int = 1000
    # data_source: Optional[DataSourceBase] = DefaultDataSource

    model_config = ConfigDict(arbitrary_types_allowed=True)
