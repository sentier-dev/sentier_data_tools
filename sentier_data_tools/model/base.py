import itertools
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date
from typing import Optional

import pandas as pd

from sentier_data_tools.iri import FlowIRI, GeonamesIRI, ProductIRI, VocabIRI
from sentier_data_tools.local_storage.db import Dataset
from sentier_data_tools.local_storage.fields import DatasetKind
from sentier_data_tools.logs import stdout_feedback_logger as logger
from sentier_data_tools.model.arguments import Demand, Flow, RunConfig


class SentierModel(ABC):
    def __init__(self, demand: Demand, run_config: RunConfig):
        self.demand = demand
        self.timeline = defaultdict(list)
        self.run_config = run_config
        if self.demand.begin_date is None:
            self.demand.begin_date = date(date.today().year - 5, 1, 1)
        if self.demand.end_date is None:
            self.demand.end_date = date(date.today().year + 4, 1, 1)
        self.validate_needs_provides()
        self.inject_needs_provides_into_class()

    def add_edges(
        self,
        dataframe: pd.DataFrame,
        column_metadata: list,
        assembly: str,
        weighting_column: Optional[str] = None,
    ) -> None:
        for column_name in dataframe.columns:
            # TODO: Use timestamp column to determine temporal bounds
            # TODO: Use location column to determine spatial bounds

            if column_name in self.needs_reverse:
                column_name = self.needs_reverse[column_name]
            if column_name in self.provides_reverse:
                column_name = self.provides_reverse[column_name]

            series = dataframe[column_name]
            if len(series) > 1 and weighting_column:
                weighted = series * dataframe[weighting_column]
                weights = weighted / weighted.dropna().sum()
                value = (series * weights).mean()
            else:
                value = series.mean()
            # self.timeline[assembly].append(
            #     Demand(
            #         product_iri: ProductIRI
            #         unit_iri: UnitIRI
            #         amount: float
            #         spatial_context: GeonamesIRI = GeonamesIRI("https://sws.geonames.org/6295630/")
            #         properties: Optional[list] = None
            #         begin_date: Optional[date] = None
            #         end_date: Optional[date] = None
            #     )
            # )

    def validate_needs_provides(self):
        if not isinstance(self.needs, dict):
            raise ValueError(f"`needs` must be a `dict`; got {type(self.needs)}")
        if not isinstance(self.provides, dict):
            raise ValueError(f"`provides` must be a `dict`; got {type(self.provides)}")
        for elem in self.needs:
            if not isinstance(elem, VocabIRI):
                raise ValueError(
                    f"Every term in `needs` must be an instance of `VocabIRI`; got {type(elem)}"
                )
        for elem in self.provides:
            if not isinstance(elem, VocabIRI):
                raise ValueError(
                    f"Every term in `provides` must be an instance of `VocabIRI`; got {type(elem)}"
                )
        if len(set(self.needs.values())) != len(self.needs):
            raise ValueError("Duplicates alias labels in `needs`")
        if len(set(self.provides.values())) != len(self.provides):
            raise ValueError("Duplicates alias labels in `provides`")
        self.provides_reverse = {v: k for k, v in self.provides.items()}
        self.needs_reverse = {v: k for k, v in self.needs.items()}

    def inject_needs_provides_into_class(self) -> None:
        for key, value in itertools.chain(self.needs.items(), self.provides.items()):
            if getattr(self, key, None) == value:
                continue
            elif hasattr(self, value):
                if hasattr(self, f"var_{value}"):
                    raise ValueError(
                        f"Alias `{value}` conflicts with existing attribute"
                    )
                logger.info(f"Changing alias `{value}` to `var_{value}`")
                setattr(self, f"var_{value}", key)
            else:
                setattr(self, value, key)

    # def prepare(self) -> None:
    #     self.get_model_data()
    #     self.data_validity_checks()
    #     self.resample()

    # @abstractmethod
    def data_validity_checks(self) -> None:
        pass

    @abstractmethod
    def run(self) -> tuple[list[Demand], list[Flow]]:
        pass

    def get_model_data(
        self,
        product: VocabIRI,
        kind: DatasetKind,
        relabel_columns: bool = True,
    ) -> dict:
        results = {
            "exactMatch": list(
                Dataset.select().where(
                    Dataset.kind == kind,
                    Dataset.product == str(product),
                )
            ),
            "broader": list(
                Dataset.select().where(
                    Dataset.kind == kind,
                    Dataset.product << product.broader(raw_strings=True),
                )
            ),
            "narrower": list(
                Dataset.select().where(
                    Dataset.kind == kind,
                    Dataset.product << product.narrower(raw_strings=True),
                )
            ),
        }
        if relabel_columns:
            for ds in itertools.chain(*results.values()):
                ds.dataframe.rename(
                    columns={str(k): v for k, v in self.provides.items()}, inplace=True
                )
                ds.dataframe.rename(
                    columns={str(k): v for k, v in self.needs.items()}, inplace=True
                )
        return results

    def merge_datasets_to_dataframes(self, lst: list[Dataset]) -> pd.DataFrame:
        if not lst:
            return pd.DataFrame()
        elif len(lst) == 1:
            return lst[0].dataframe
        else:
            given = lst.pop(0).dataframe
            while lst:
                given = pd.merge(given, lst.pop(0).dataframe, how="outer")
            return given
