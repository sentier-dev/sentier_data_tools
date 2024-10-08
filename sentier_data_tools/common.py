from typing import Optional
from pydantic import BaseModel
import pandas as pd
from datetime import date

from sentier_data_tools.iri import ProductIRI, GeonamesIRI


class Demand(BaseModel):
    product_iri: ProductIRI
    properties: Optional[list]
    amount: float
    spatial_context: GeonamesIRI = GeonamesIRI("https://sws.geonames.org/6295630/")
    begin_date: Optional[date] = None
    end_date: Optional[date] = None


class RunConfig(BaseModel):
    num_samples: int = 1000


class SentierModel:
    def __init__(self, demand: Demand, run_config: RunConfig):
        self.demand = demand
        self.run_config = run_config
        if self.run_config.begin_date is None:
            self.run_config.begin_date = date(date.today().year - 5, 1, 1)
        if self.run_config.end_date is None:
            self.run_config.end_date = date(date.today().year + 5, 1, 1)

    def get_model_data(self) -> list[pd.DataFrame]:
        pass

    def prepare(self) -> None:
        self.get_model_data()
        self.data_validity_checks()
        self.resample()

    def run(self) -> list[Demand]:
        pass

