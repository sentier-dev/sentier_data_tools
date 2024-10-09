from abc import ABC, abstractmethod
from datetime import date

import pandas as pd

from sentier_data_tools.iri import FlowIRI, GeonamesIRI, ProductIRI
from sentier_data_tools.local_storage.db import Dataframe
from sentier_data_tools.local_storage.fields import DataframeKind
from sentier_data_tools.model.arguments import Demand, Flow, RunConfig


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

    @property
    def _provides_str(self):
        return {str(elem) for elem in self.provides}

    @property
    def _needs_str(self):
        return {str(elem) for elem in self.needs}

    @property
    def _needs_narrower(self):
        return {
            str(other)
            for elem in self.needs
            for other in elem.narrower(raw_strings=True)
        }

    @property
    def _needs_broader(self):
        return {
            str(other)
            for elem in self.needs
            for other in elem.broader(raw_strings=True)
        }

    def get_model_data(self) -> dict:
        return {
            DataframeKind.BOM: {
                "exactMatch": Dataframe.select().where(
                    Dataframe.kind == DataframeKind.BOM,
                    Dataframe.product << self._needs_str,
                ),
                "broader": Dataframe.select().where(
                    Dataframe.kind == DataframeKind.BOM,
                    Dataframe.product << self._needs_broader,
                ),
                "narrower": Dataframe.select().where(
                    Dataframe.kind == DataframeKind.BOM,
                    Dataframe.product << self._needs_narrower,
                ),
            },
            DataframeKind.PARAMETERS: {
                "exactMatch": Dataframe.select().where(
                    Dataframe.kind == DataframeKind.PARAMETERS,
                    Dataframe.product << self._needs_str,
                ),
                "broader": Dataframe.select().where(
                    Dataframe.kind == DataframeKind.PARAMETERS,
                    Dataframe.product << self._needs_broader,
                ),
                "narrower": Dataframe.select().where(
                    Dataframe.kind == DataframeKind.PARAMETERS,
                    Dataframe.product << self._needs_narrower,
                ),
            },
        }
