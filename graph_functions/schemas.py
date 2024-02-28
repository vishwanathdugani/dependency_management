from typing import Dict, List, Any
from pydantic import BaseModel, validator


class Dependency(BaseModel):
    """
    Represents a package dependency with optional alternatives.
    """
    name: str
    alternatives: List[str] = []

    def __hash__(self):
        """Enables Dependency objects to be used as hashable items in sets."""
        return hash((self.name, tuple(self.alternatives)))


class PackageInfo(BaseModel):
    """
    Contains information about a package including its name, description, and dependencies.
    """
    Package: str
    Description: str
    Depends: List[Dependency] = []

    @validator('Depends', pre=True, allow_reuse=True)
    def split_depends(cls, v):
        """Splits and formats the dependency field into a list of Dependency objects."""
        if not v:
            return []
        dependencies = []
        for dep in v.split(','):
            parts = [part.strip() for part in dep.split('|')]
            main_dep, alternatives = parts[0], parts[1:]
            dependencies.append(Dependency(name=main_dep, alternatives=alternatives))
        return dependencies


class PackageResponseModel(BaseModel):
    package: str
    description: str


class PackageDetailsModel(BaseModel):
    package: str
    description: str
    direct_dependencies: List[str]
    # indirect_dependencies: List[HttpUrl]
    direct_reverse_dependencies: List[str]
    # indirect_reverse_dependencies: List[HttpUrl]
    alternatives: Dict[str, Any]