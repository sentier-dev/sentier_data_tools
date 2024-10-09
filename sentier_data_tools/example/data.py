from datetime import date
from pathlib import Path

import pandas as pd
from loguru import logger

import sentier_data_tools as sdt


def create_example_local_datastorage(reset: bool = True):
    if reset:
        sdt.reset_local_database()

    df = pd.read_excel(Path(__file__).parent / "electrolyzers.xlsx")
    assert len(COLUMNS) == len(UNITS)
    assert len(COLUMNS) == len(df.columns) - 1

    metadata = sdt.Datapackage(
        name="electrolyzer data from Premise 2024",
        description="Electrolyzer operation and construction inventory data taken from Premise in April 2024.",
        contributors=[
            {
                "title": "Karin Treyer",
                "path": "https://www.psi.ch/en/ta/people/karin-treyer",
                "role": "author",
            },
            {
                "title": "Chris Mutel",
                "path": "https://chris.mutel.org/",
                "role": "wrangler",
            },
        ],
        homepage="https://github.com/polca/premise/tree/master/premise/data/additional_inventories",
    ).metadata()
    metadata.pop("version")

    for kind, iri in TYPES:
        filtered = df[df["Electrolysis type"] == kind].copy()
        logger.info("Adding {} records for type {}", len(filtered), kind)
        filtered.drop(labels=["Electrolysis type"], axis="columns", inplace=True)
        filtered.columns = COLUMNS

        sdt.Dataset(
            name=f"electrolyser model data for {kind.lower()}",
            dataframe=filtered,
            product=iri,
            columns=[{"iri": x, "unit": y} for x, y in zip(COLUMNS, UNITS)],
            metadata=metadata,
            location="https://sws.geonames.org/6255148/",
            version=1,
            valid_from=date(2018, 1, 1),
            valid_to=date(2028, 1, 1),
        ).save()

    for key, value in LIFETIMES.items():
        sdt.Dataset(
            name="Estimated electrolyzer BoP (balance of plant) lifetimes",
            dataframe=pd.DataFrame([{key: value}]),
            product=key,
            columns=[
                {
                    "iri": "https://vocab.sentier.dev/model-terms/electrolyser/product_lifetime",
                    "unit": "https://vocab.sentier.dev/units/unit/YR",
                }
            ],
            location="https://sws.geonames.org/6255148/",
            metadata=metadata,
            version=1,
            valid_from=date(2018, 1, 1),
            valid_to=date(2028, 1, 1),
        ).save()

    sdt.Dataset(
        name="Estimated PEM electrolyzer Stack materials",
        dataframe=pd.DataFrame(PEM_STACK),
        product="https://vocab.sentier.dev/products/pem-electrolyzer",
        columns=PEM_STACK_COLUMNS,
        location="https://sws.geonames.org/6255148/",
        metadata=metadata
        | {
            "determining_value": "https://vocab.sentier.dev/model-terms/energy/nom_power_cons"
        },
        version=1,
        kind=sdt.DatasetKind.BOM,
        valid_from=date(2018, 1, 1),
        valid_to=date(2028, 1, 1),
    ).save()

    sdt.Dataset(
        name="electrolysis water consumption value",
        dataframe=pd.DataFrame(
            [
                {
                    "http://data.europa.eu/xsp/cn2024/285390100080": 14.0,
                    "http://openenergy-platform.org/ontology/oeo/OEO_00010379": 1.0,
                },
            ]
        ),
        product="http://openenergy-platform.org/ontology/oeo/OEO_00010379",
        columns=[
            {
                "iri": "http://data.europa.eu/xsp/cn2024/285390100080",
                "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
            },
            {
                "iri": "http://openenergy-platform.org/ontology/oeo/OEO_00010379",
                "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
            },
        ],
        metadata={
            "description": "...water needs per kg of H2 are reported.. ranging from 10.01 to 22.40 l per kg of H2.",
            "homepage": "https://www.sciencedirect.com/science/article/abs/pii/S0959652621023428",
            "contributors": [
                {
                    "title": "Sofia Simoes",
                    "path": "https://orcid.org/0000-0003-4304-1411",
                    "role": "author",
                },
                {
                    "title": "Chris Mutel",
                    "path": "https://chris.mutel.org/",
                    "role": "wrangler",
                },
            ],
            "determining_value": "http://openenergy-platform.org/ontology/oeo/OEO_00010379",
        },
        version=1,
        kind=sdt.DatasetKind.BOM,
        valid_from=date(2018, 1, 1),
        valid_to=date(2028, 1, 1),
    ).save()


COLUMNS = [
    "https://vocab.sentier.dev/model-terms/generic/company",
    "https://vocab.sentier.dev/model-terms/generic/product",
    "https://vocab.sentier.dev/model-terms/energy/min_power_cons",
    "https://vocab.sentier.dev/model-terms/energy/nom_power_cons",
    "https://vocab.sentier.dev/model-terms/energy/max_power_cons",
    "https://vocab.sentier.dev/model-terms/energy/input_voltage",
    "https://vocab.sentier.dev/model-terms/generic/footprint_area",
    "https://vocab.sentier.dev/model-terms/generic/availability",
    "https://vocab.sentier.dev/model-terms/electrolyzer/min_amb_temp",
    "https://vocab.sentier.dev/model-terms/electrolyzer/max_amb_temp",
    "https://vocab.sentier.dev/model-terms/energy/elec_energy_serv_dem",
    "https://vocab.sentier.dev/model-terms/energy/therm_energy_serv_dem",
    "https://vocab.sentier.dev/model-terms/energy/therm_energy_conv_eff",
    "https://vocab.sentier.dev/model-terms/electrolyzer/temp_useful_heat",
    "https://vocab.sentier.dev/model-terms/energy/energy_conv_eff_lhv",
    "http://openenergy-platform.org/ontology/oeo/OEO_00140049",
    "https://vocab.sentier.dev/model-terms/electrolyzer/min_stack_temp",
    "https://vocab.sentier.dev/model-terms/electrolyzer/max_stack_temp",
    "https://vocab.sentier.dev/model-terms/electrolyzer/max_water_conduc",
    "https://vocab.sentier.dev/model-terms/electrolyser/max_stack_lifetime",
    "https://vocab.sentier.dev/model-terms/electrolyser/h2_quality",
    "https://vocab.sentier.dev/model-terms/electrolyser/h2_pressure",
    "https://vocab.sentier.dev/model-terms/generic/mass_prod_rate",
]

UNITS = [
    "https://www.w3.org/2001/XMLSchema#string",
    "https://www.w3.org/2001/XMLSchema#string",
    "https://vocab.sentier.dev/units/unit/KiloW",
    "https://vocab.sentier.dev/units/unit/KiloW",
    "https://vocab.sentier.dev/units/unit/KiloW",
    "https://vocab.sentier.dev/units/unit/V",
    "https://vocab.sentier.dev/units/unit/M2",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/DEG_C",
    "https://vocab.sentier.dev/units/unit/DEG_C",
    "https://vocab.sentier.dev/units/unit/KiloW-HR-PER-KiloGM",
    "https://vocab.sentier.dev/units/unit/MegaJ-PER-KiloGM",
    "https://vocab.sentier.dev/units/unit/FRACTION",
    "https://vocab.sentier.dev/units/unit/DEG_C",
    "https://vocab.sentier.dev/units/unit/PERCENT",
    "https://vocab.sentier.dev/units/unit/PERCENT",
    "https://vocab.sentier.dev/units/unit/DEG_C",
    "https://vocab.sentier.dev/units/unit/DEG_C",
    "https://vocab.sentier.dev/units/unit/MicroS-PER-CentiM",
    "https://vocab.sentier.dev/units/unit/HR",
    "https://vocab.sentier.dev/units/unit/NUM",
    "https://vocab.sentier.dev/units/unit/PA",
    "https://vocab.sentier.dev/units/unit/KiloGM-PER-HR",
]

TYPES = [
    ("PEM", "https://vocab.sentier.dev/products/pem-electrolyzer"),
    ("AEC", "https://vocab.sentier.dev/products/aec-electrolyzer"),
    ("SOEC", "https://vocab.sentier.dev/products/soel-electrolyzer"),
]

LIFETIMES = {
    "https://vocab.sentier.dev/products/pem-electrolyzer": 20,
    "https://vocab.sentier.dev/products/aec-electrolyzer": 27.5,
    "https://vocab.sentier.dev/products/soel-electrolyzer": 20,
}

PEM_STACK = [
    {
        "https://vocab.sentier.dev/model-terms/electrolyser/stack": 1.00,
        "http://data.europa.eu/xsp/cn2024/760611000010": 27.00,
        "http://data.europa.eu/xsp/cn2024/810890500080": 528.00,
        "https://vocab.sentier.dev/products/tetrafluoroethylene": 16.00,
        "http://data.europa.eu/xsp/cn2024/280300000080": 4.50,
        "http://data.europa.eu/xsp/cn2024/711041000010": 0.80,
        "http://data.europa.eu/xsp/cn2024/711019100080": 0.08,
        "http://data.europa.eu/xsp/cn2024/280300000080": 4.50,
        "http://data.europa.eu/xsp/cn2024/740900000080": 4.50,
        "http://data.europa.eu/xsp/cn2024/722000000080": 100.00,
        "http://data.europa.eu/xsp/cn2024/401693000080": 4.80,
        "http://data.europa.eu/xsp/cn2024/271600000080": 103890.77,
    }
]
PEM_STACK_COLUMNS = [
    {
        "iri": "https://vocab.sentier.dev/model-terms/energy/nom_power_cons",
        "unit": "https://vocab.sentier.dev/units/unit/MegaW",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/760611000010",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "assembly": "end plate",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/810890500080",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "assembly": "bipolar plate",
    },
    {
        "iri": "https://vocab.sentier.dev/products/tetrafluoroethylene",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "comment": "membrane polymer",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/280300000080",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "assembly": "electrocatalyst anode",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/711041000010",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "assembly": "electrocatalyst anode",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/711019100080",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "assembly": "electrocatalyst cathode",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/280300000080",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "assembly": "electrocatalyst cathode",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/740900000080",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "assembly": "current collector",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/722000000080",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "comment": "bolts and screws",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/401693000080",
        "unit": "https://vocab.sentier.dev/units/unit/KiloGM",
        "comment": "gasket",
    },
    {
        "iri": "http://data.europa.eu/xsp/cn2024/271600000080",
        "unit": "https://vocab.sentier.dev/units/unit/KiloW-HR",
        "comment": "assembly energy",
    },
]
