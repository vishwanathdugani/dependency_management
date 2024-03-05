from typing import Dict, Set, List
from pydantic import ValidationError
import re
from graph_functions.schemas import PackageInfo


class DependenciesHelper:
    def __init__(self):
        self.dependencies_graph: Dict[str, PackageInfo] = {}
        self.reverse_dependencies_graph: Dict[str, Set[str]] = {}

    def build_graphs(self, content: str):
        """
        Parses package data from a given string and builds forward and reverse dependency graphs.
        """
        self.dependencies_graph.clear()
        self.reverse_dependencies_graph.clear()

        packages = content.split('\n\n')
        for block in packages:
            try:
                package_data = {
                    match.group(1): match.group(2)
                    for match in re.finditer(r'^(.*): (.*)$', block, re.M)
                }
                if 'Package' in package_data and 'Description' in package_data:
                    package_info = PackageInfo.parse_obj(package_data)
                    self.dependencies_graph[package_info.Package] = package_info
                    for dep in package_info.Depends:
                        self.reverse_dependencies_graph.setdefault(dep.name, set()).add(package_info.Package)
            except ValidationError as e:
                print(f"Error parsing package info: {e}")

    def find_dependencies(self, package_name: str, visited: Set[str] = None, forward=True) -> Set[str]:
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
            graph = self.dependencies_graph
            get_deps = lambda pkg: {dep.name for dep in graph[pkg].Depends}
        else:
            graph = self.reverse_dependencies_graph
            get_deps = graph.get

        if package_name in graph:
            direct_deps = get_deps(package_name)
            for dep_name in direct_deps:
                all_deps.add(dep_name)
                all_deps.update(self.find_dependencies(dep_name, visited, forward))

        return all_deps

    def get_package_details(self, package_name: str) -> Dict:
        """
        Retrieves detailed information about a package, including dependencies and reverse dependencies.
        """
        package_info = self.dependencies_graph.get(package_name)
        if not package_info:
            return {}

        direct_deps_info = [f"{dep.name}" for dep in package_info.Depends]
        alternatives_info = {
            dep.name: [f"{alt}" for alt in dep.alternatives]
            for dep in package_info.Depends if dep.alternatives
        }
        all_deps = self.find_dependencies(package_name, visited=set())
        direct_deps_names = {dep.name for dep in package_info.Depends}
        indirect_deps_names = all_deps - direct_deps_names - {package_name}
        indirect_deps_info = [f"{dep}" for dep in indirect_deps_names]

        direct_reverse_deps = self.reverse_dependencies_graph.get(package_name, set())
        indirect_reverse_deps = self.find_dependencies(package_name, forward=False) - direct_reverse_deps - {package_name}

        return {
            "package": package_info.Package,
            "description": package_info.Description,
            "direct_dependencies": direct_deps_info,
            "indirect_dependencies": indirect_deps_info,
            "direct_reverse_dependencies": [f"{dep}" for dep in direct_reverse_deps],
            "indirect_reverse_dependencies": [f"{dep}" for dep in indirect_reverse_deps],
            "alternatives": alternatives_info
        }

    def get_packages_with_no_dependencies(self) -> List[str]:
        """
        Returns a list of packages that have no dependencies.
        """
        return [pkg for pkg, details in self.dependencies_graph.items() if not details.Depends]
