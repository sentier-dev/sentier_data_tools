import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import pandas as pd

from sentier_data_tools.datapackage.validation import Contributors, DatapackageMetadata
from sentier_data_tools.licenses import LICENSES


class Datapackage:
    def __init__(
        self,
        *,
        name: str,
        description: str,
        contributors: list,
        homepage: Optional[str] = None,
        created: Optional[datetime] = None,
        version: str = "1",
        licenses: Optional[list] = None,
    ):
        self.name = name
        self.description = description
        self.contributors = contributors
        self.homepage = homepage
        self.created = created or datetime.now(timezone.utc).isoformat()
        self.licenses = licenses or [LICENSES["CC-BY-4.0"]]
        self.version = version
        self.resources = {}

        for contributor in contributors:
            Contributors(**contributor)
        DatapackageMetadata(
            name=self.name,
            description=self.description,
            homepage=self.homepage,
            created=self.created,
            version=self.version,
            licenses=self.licenses,
        )

    def metadata(self) -> dict:
        data = {
            "name": self.name,
            "description": self.description,
            "contributors": self.contributors,
            "created": self.created.isoformat()
            if isinstance(self.created, datetime)
            else self.created,
            "version": self.version,
            "licenses": self.licenses,
        }
        if self.homepage:
            data["homepage"] = self.homepage
        return data

    def add_resource(
        self, dataframe: pd.DataFrame, units: List[str], logs: Optional[list] = None
    ) -> None:
        pass

    def to_json(self, filepath: Path) -> Path:
        if not isinstance(filepath, Path):
            filepath = Path(filepath)
        if filepath.suffix.lower() != ".json":
            filepath = filepath.parent / f"{filepath.name}.json"
        if not os.access(filepath.parent, os.W_OK):
            raise OSError(f"Can't write to directory {filepath.parent}")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.metadata() | self.data(), f, indent=2, ensure_ascii=False)

        return filepath
