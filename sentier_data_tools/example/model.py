from sentier_data_tools import (
    DatasetKind,
    Demand,
    Flow,
    FlowIRI,
    GeonamesIRI,
    ModelTermIRI,
    ProductIRI,
    SentierModel,
)
from sentier_data_tools.logs import stdout_feedback_logger as logger


class WaterElectrolysisModel(SentierModel):
    provides = {
        ProductIRI(
            "http://openenergy-platform.org/ontology/oeo/OEO_00010379"
        ): "hydrogen",
    }
    needs = {
        ModelTermIRI(
            "https://vocab.sentier.dev/model-terms/electrolyser/capacity_factor"
        ): "capacity_factor",
        ModelTermIRI(
            "https://vocab.sentier.dev/model-terms/electrolyser/product_lifetime"
        ): "lifetime",
        ModelTermIRI(
            "https://vocab.sentier.dev/model-terms/energy/elec_energy_serv_dem"
        ): "elec_energy_serv_dem",
        ProductIRI("https://vocab.sentier.dev/products/electrolyzer"): "electrolyzer",
    }

    def get_electrolysis_inventory(self) -> None:
        bom_electrolysis = self.get_model_data(
            self, product=self.hydrogen, kind=DatasetKind.BOM
        )

    def run(self) -> tuple[list[Demand], list[Flow]]:
        self.prepare()

    # def prepare(self) -> None:
    #     self.get_model_data()
    #     self.data_validity_checks()
    #     self.resample()

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
