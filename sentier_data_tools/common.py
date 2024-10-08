from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

import pandas as pd
from pydantic import BaseModel

from sentier_data_tools.data_source_base import DataSourceBase
from sentier_data_tools.iri import FlowIRI, GeonamesIRI, ProductIRI
from sentier_data_tools.local_data_store import DefaultDataSource


class Demand(BaseModel):
    product_iri: ProductIRI
    properties: Optional[list]
    amount: float
    spatial_context: GeonamesIRI = GeonamesIRI("https://sws.geonames.org/6295630/")
    begin_date: Optional[date] = None
    end_date: Optional[date] = None


class Flow(BaseModel):
    flow_iri: FlowIRI


class RunConfig(BaseModel):
    num_samples: int = 1000
    data_source: Optional[DataSourceBase] = DefaultDataSource


class SentierModel(ABC):
    def __init__(self, demand: Demand, run_config: RunConfig):
        self.demand = demand
        self.run_config = run_config
        if self.run_config.begin_date is None:
            self.run_config.begin_date = date(date.today().year - 5, 1, 1)
        if self.run_config.end_date is None:
            self.run_config.end_date = date(date.today().year + 4, 1, 1)

    def get_model_data(self, abbreviate_iris: bool = True) -> list[pd.DataFrame]:
        pass

    def prepare(self, abbreviate_iris: bool = True) -> None:
        self.get_model_data(abbreviate_iris=abbreviate_iris)
        self.data_validity_checks()
        self.resample()

    @abstractmethod
    def data_validity_checks(self) -> None:
        pass

    @abstractmethod
    def run(self) -> tuple[list[Demand], list[Flow]]:
        pass
