import itertools
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
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
            self.demand.begin_date = datetime(datetime.today().year - 5, 1, 1)
        if self.demand.end_date is None:
            self.demand.end_date = datetime(datetime.today().year + 4, 1, 1)
        self.validate_aliases()
        self.inject_aliases()

    def add_edges(
        self,
        dataframe: pd.DataFrame,
        column_metadata: list,
        assembly: str,
        weighting_column: Optional[str] = None,
    ) -> None:
        # TODO: Start over
        # for column_name in dataframe.columns:
        #     # TODO: Use timestamp column to determine temporal bounds
        #     # TODO: Use location column to determine spatial bounds

        #     if column_name in self.needs_reverse:
        #         column_name = self.needs_reverse[column_name]
        #     if column_name in self.provides_reverse:
        #         column_name = self.provides_reverse[column_name]

        #     series = dataframe[column_name]
        #     if len(series) > 1 and weighting_column:
        #         weighted = series * dataframe[weighting_column]
        #         weights = weighted / weighted.dropna().sum()
        #         value = (series * weights).mean()
        #     else:
        #         value = series.mean()
        #     # self.timeline[assembly].append(
        #     #     Demand(
        #     #         product_iri: ProductIRI
        #     #         unit_iri: UnitIRI
        #     #         amount: float
        #     #         spatial_context: GeonamesIRI = GeonamesIRI("https://sws.geonames.org/6295630/")
        #     #         properties: Optional[list] = None
        #     #         begin_date: Optional[datetime] = None
        #     #         end_date: Optional[datetime] = None
        #     #     )
        #     # )
        ...

    def validate_aliases(self):
        if not isinstance(self.aliases, dict):
            raise ValueError(f"`aliases` must be a `dict`; got {type(self.aliases)}")
        for elem in self.aliases:
            if not isinstance(elem, VocabIRI):
                raise ValueError(
                    f"Every term in `aliases` must be an instance of `VocabIRI`; got {type(elem)}"
                )
        if len(set(self.aliases.values())) != len(self.aliases):
            raise ValueError("Duplicates alias labels")

    def inject_aliases(self) -> None:
        for key, value in self.aliases.items():
            # Skip existing attribute
            if getattr(self, key, None) == value:
                continue
            elif hasattr(self, value):
                logger.warning(
                    "Can't apply alias %s because it's already a class attribute", key
                )
                continue
            else:
                setattr(self, value, key)

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
        for df in itertools.chain(*results.values()):
            df.dataframe.apply_aliases(self.aliases)

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
