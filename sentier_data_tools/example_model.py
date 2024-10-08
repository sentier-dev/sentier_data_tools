from sentier_data_tools.common import Demand, Flow, SentierModel
from sentier_data_tools.iri import FlowIRI, GeonamesIRI, ProductIRI
from sentier_data_tools.logs import stdout_feedback_logger


class Electrolyzer(SentierModel):
    provides = [ProductIRI("http://data.europa.eu/xsp/cn2024/280410000080")]
    needs = []

    def run(self, abbreviate_iris: bool = True) -> tuple[list[Demand], list[Flow]]:
        self.prepare()

    def prepare(self) -> None:
        self.get_model_data()
        self.data_validity_checks()
        self.resample()
