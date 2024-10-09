from abc import ABC, abstractmethod
from datetime import date

import pandas as pd

from sentier_data_tools.iri import FlowIRI, GeonamesIRI, ProductIRI, VocabIRI
from sentier_data_tools.local_storage.db import Dataset
from sentier_data_tools.local_storage.fields import DatasetKind
from sentier_data_tools.model.arguments import Demand, Flow, RunConfig


class SentierModel(ABC):
    def __init__(self, demand: Demand, run_config: RunConfig):
        self.demand = demand
        self.run_config = run_config
        if self.demand.begin_date is None:
            self.demand.begin_date = date(date.today().year - 5, 1, 1)
        if self.demand.end_date is None:
            self.demand.end_date = date(date.today().year + 4, 1, 1)
        self.validate_needs_provides()

    def validate_needs_provides(self):
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
        if isinstance(self.needs, dict) and len(set(self.needs.values())) != len(
            self.needs
        ):
            raise ValueError("Duplicates alias labels in `needs`")
        if isinstance(self.provides, dict) and len(set(self.provides.values())) != len(
            self.provides
        ):
            raise ValueError("Duplicates alias labels in `provides`")

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

    @property
    def _provides_str(self):
        return {str(elem) for elem in self.provides}

    @property
    def _provides_narrower(self):
        return {
            str(other)
            for elem in self.provides
            for other in elem.narrower(raw_strings=True)
        }

    @property
    def _provides_broader(self):
        return {
            str(other)
            for elem in self.provides
            for other in elem.broader(raw_strings=True)
        }

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

    def get_model_data(self, product: VocabIRI, kind: DatasetKind) -> dict:
        return {
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
