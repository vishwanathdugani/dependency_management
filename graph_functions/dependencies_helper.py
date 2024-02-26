from typing import Dict, Set, List, Union
from pydantic import BaseModel, ValidationError, validator
import re


class Dependency(BaseModel):
    """
    Represents a package dependency with optional alternatives.
    """
    name: str
    alternatives: List[str] = []

    def __hash__(self):
        """Enables Dependency objects to be used as hashable items in sets."""
        return hash((self.name, tuple(self.alternatives)))

    def __eq__(self, other):
        """Checks equality with another Dependency object."""
        if not isinstance(other, Dependency):
            return NotImplemented
        return self.name == other.name and self.alternatives == other.alternatives


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


dependencies_graph: Dict[str, PackageInfo] = {}
reverse_dependencies_graph: Dict[str, Set[str]] = {}


def build_graphs(content: str):
    """
    Parses package data from a given string and builds forward and reverse dependency graphs.
    """
    global dependencies_graph, reverse_dependencies_graph
    dependencies_graph.clear()
    reverse_dependencies_graph.clear()

    packages = content.split('\n\n')
    for block in packages:
        try:
            package_data = {
                match.group(1): match.group(2)
                for match in re.finditer(r'^(.*): (.*)$', block, re.M)
            }
            if 'Package' in package_data and 'Description' in package_data:
                package_info = PackageInfo.parse_obj(package_data)
                dependencies_graph[package_info.Package] = package_info
                for dep in package_info.Depends:
                    reverse_dependencies_graph.setdefault(dep.name, set()).add(package_info.Package)
        except ValidationError as e:
            print(f"Error parsing package info: {e}")


def find_all_dependencies(package_name: str, visited: Set[str] = None) -> Set[str]:
    """
    Finds all dependencies for a given package, optionally limiting to direct dependencies.
    """
    if visited is None:
        visited = set()
    if package_name in visited:
        return set()
    visited.add(package_name)
    all_deps = set()
    if package_name in dependencies_graph:
        direct_deps = {dep.name for dep in dependencies_graph[package_name].Depends}
        for dep_name in direct_deps:
            all_deps.add(dep_name)
            all_deps.update(find_all_dependencies(dep_name, visited))
    return all_deps


def find_all_reverse_dependencies(package_name: str, visited: Set[str] = None) -> Set[str]:
    """
    Finds all packages that depend on the given package, including indirect dependencies.
    """
    if visited is None:
        visited = set()
    if package_name in visited:
        return set()
    visited.add(package_name)
    all_deps = set()
    if package_name in reverse_dependencies_graph:
        direct_deps = reverse_dependencies_graph[package_name]
        for dep in direct_deps:
            all_deps.add(dep)
            all_deps.update(find_all_reverse_dependencies(dep, visited))
    return all_deps


def get_package_details(package_name: str, base_url: str) -> Dict:
    """
    Retrieves detailed information about a package, including dependencies and reverse dependencies.
    """
    package_info = dependencies_graph.get(package_name)
    if not package_info:
        return {}

    direct_deps_info = [f"{base_url}/package/{dep.name}" for dep in package_info.Depends]
    alternatives_info = {
        dep.name: [f"{base_url}/package/{alt}" for alt in dep.alternatives]
        for dep in package_info.Depends if dep.alternatives
    }
    all_deps = find_all_dependencies(package_name, visited=set())
    direct_deps_names = {dep.name for dep in package_info.Depends}
    indirect_deps_names = all_deps - direct_deps_names - {package_name}
    indirect_deps_info = [f"{base_url}/package/{dep}" for dep in indirect_deps_names]

    direct_reverse_deps = reverse_dependencies_graph.get(package_name, set())
    indirect_reverse_deps = find_all_reverse_dependencies(package_name) - direct_reverse_deps - {package_name}

    return {
        "package": package_info.Package,
        "description": package_info.Description,
        "direct_dependencies": direct_deps_info,
        "indirect_dependencies": indirect_deps_info,
        "direct_reverse_dependencies": [f"{base_url}/package/{dep}" for dep in direct_reverse_deps],
        "indirect_reverse_dependencies": [f"{base_url}/package/{dep}" for dep in indirect_reverse_deps],
        "alternatives": alternatives_info
    }


def get_packages_with_no_dependencies() -> List[str]:
    """
    Returns a list of packages that have no dependencies.
    """
    return [pkg for pkg, details in dependencies_graph.items() if not details.Depends]
