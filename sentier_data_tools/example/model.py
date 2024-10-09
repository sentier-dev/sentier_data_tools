from sentier_data_tools import (
    Demand,
    Flow,
    FlowIRI,
    GeonamesIRI,
    ModelTermIRI,
    ProductIRI,
    SentierModel,
)
from sentier_data_tools.logs import stdout_feedback_logger


class ElectrolyzerModel(SentierModel):
    provides = [ProductIRI("http://data.europa.eu/xsp/cn2024/280410000080")]
    needs = [
        ModelTermIRI(
            "https://vocab.sentier.dev/model-terms/electrolyser/capacity_factor"
        ),
        ModelTermIRI(
            "https://vocab.sentier.dev/model-terms/electrolyser/product_lifetime"
        ),
    ]

    def run(self) -> tuple[list[Demand], list[Flow]]:
        self.prepare()

    def prepare(self) -> None:
        self.get_model_data()
        self.data_validity_checks()
        self.resample()

    # Calculate bill of materials for main product
    # Pull in BOM data for hydrogen

    # def get_model_data(self) -> list[pd.DataFrame]:
    #     pass

    # def prepare(self) -> None:
    #     self.get_model_data(abbreviate_iris=abbreviate_iris)
    #     self.data_validity_checks()
    #     self.resample()

    # @abstractmethod
    # def data_validity_checks(self) -> None:
    #     pass

    # @abstractmethod
    # def run(self) -> tuple[list[Demand], list[Flow]]:
    #     pass
