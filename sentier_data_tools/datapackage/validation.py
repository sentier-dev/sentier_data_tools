from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class Contributors(BaseModel):
    title: str
    role: str
    path: str


class DatapackageMetadata(BaseModel):
    """Validate given Datapackage metadata.

    Pydantic gives us nice error messages for free."""

    name: str
    description: str
    homepage: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    version: str
    licenses: List[Dict[str, str]]
