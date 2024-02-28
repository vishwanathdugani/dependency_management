from typing import Dict, Set, List
from pydantic import ValidationError
import re

from graph_functions.schemas import PackageInfo

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


def find_dependencies(package_name: str, visited: Set[str] = None, forward=True) -> Set[str]:
    """
    Finds all dependencies or reverse dependencies for a given package, optionally limiting to direct dependencies.
    """

    if visited is None:
        visited = set()

    if package_name in visited:
        return set()

    visited.add(package_name)
    all_deps = set()

    if forward:
        graph = dependencies_graph
        get_deps = lambda pkg: {dep.name for dep in graph[pkg].Depends}
    else:
        graph = reverse_dependencies_graph
        get_deps = graph.get

    if package_name in graph:
        direct_deps = get_deps(package_name)
        for dep_name in direct_deps:
            all_deps.add(dep_name)
            all_deps.update(find_dependencies(dep_name, visited, forward))

    return all_deps


def get_package_details(package_name: str, base_url: str) -> Dict:
    """
    Retrieves detailed information about a package, including dependencies and reverse dependencies.

     The "direct_dependencies" are packages a given package immediately requires to function,
    while "indirect_dependencies" are those needed by its direct dependencies, extending further into the graph.
    "Direct_reverse_dependencies" are packages directly dependent on the given package, and
    "indirect_reverse_dependencies" extend this concept to include all packages reliant on those directly
    dependent packages. "Alternatives" offer optional dependencies that can substitute for the primary one,
    allowing flexibility in package selection and installation.
    """
    package_info = dependencies_graph.get(package_name)
    if not package_info:
        return {}

    direct_deps_info = [f"{base_url}/package/{dep.name}" for dep in package_info.Depends]
    alternatives_info = {
        dep.name: [f"{base_url}/package/{alt}" for alt in dep.alternatives]
        for dep in package_info.Depends if dep.alternatives
    }
    all_deps = find_dependencies(package_name, visited=set())
    direct_deps_names = {dep.name for dep in package_info.Depends}
    indirect_deps_names = all_deps - direct_deps_names - {package_name}
    indirect_deps_info = [f"{base_url}/package/{dep}" for dep in indirect_deps_names]

    direct_reverse_deps = reverse_dependencies_graph.get(package_name, set())
    indirect_reverse_deps = find_dependencies(package_name, forward=False) - direct_reverse_deps - {package_name}

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
