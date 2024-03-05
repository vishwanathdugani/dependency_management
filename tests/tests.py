from graph_functions.dependencies_helper import DependenciesHelper
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
dep_helper = DependenciesHelper()


@pytest.fixture(scope="module")
def status_content():
    with open("tests/status", "r") as file:
        content = file.read()
    return content


def compare(actual, expected):
    assert actual["package"] == expected["package"]
    assert actual["description"] == expected["description"]
    assert set(actual["direct_dependencies"]) == set(expected["direct_dependencies"])
    assert set(actual["indirect_dependencies"]) == set(expected["indirect_dependencies"])
    assert set(actual["direct_reverse_dependencies"]) == set(expected["direct_reverse_dependencies"])
    assert set(actual["indirect_reverse_dependencies"]) == set(expected["indirect_reverse_dependencies"])
    return True


def test_package_a_details(status_content):
    dep_helper.build_graphs(status_content)
    package_a_expected = {
        "package": "package-a",
        "description": "Package A",
        "direct_dependencies": ["package-b"],
        "indirect_dependencies": ["package-c",
                                  "package-d",
                                  "package-e"],
        "direct_reverse_dependencies": [],
        "indirect_reverse_dependencies": [],
        "alternatives": {}
    }
    assert compare(dep_helper.get_package_details("package-a") , package_a_expected)


def test_package_b_details(status_content):
    dep_helper.build_graphs(status_content)

    package_b_expected = {
        "package": "package-b",
        "description": "Package B",
        "direct_dependencies": ["package-c", "package-d"],
        "indirect_dependencies": ["package-e"],
        "direct_reverse_dependencies": ["package-a"],
        "indirect_reverse_dependencies": [],
        "alternatives": {}
    }
    assert compare(dep_helper.get_package_details("package-b") , package_b_expected)


def test_package_c_details(status_content):
    dep_helper.build_graphs(status_content)
    package_c_expected = {
        "package": "package-c",
        "description": "Package C",
        "direct_dependencies": [],
        "indirect_dependencies": [],
        "direct_reverse_dependencies": ["package-b"],
        "indirect_reverse_dependencies": ["package-a"],
        "alternatives": {}
    }
    assert compare(dep_helper.get_package_details("package-c"), package_c_expected)


def test_package_d_details(status_content):
    dep_helper.build_graphs(status_content)
    package_d_expected = {
        "package": "package-d",
        "description": "Package D",
        "direct_dependencies": ["package-e"],
        "indirect_dependencies": [],
        "direct_reverse_dependencies": ["package-b"],
        "indirect_reverse_dependencies": ["package-a"],
        "alternatives": {"package-e": ["package-f"]}
    }
    assert compare(dep_helper.get_package_details("package-d"), package_d_expected)


def test_package_e_details(status_content):
    dep_helper.build_graphs(status_content)
    package_e_expected = {
        "package": "package-e",
        "description": "Package E",
        "direct_dependencies": [],
        "indirect_dependencies": [],
        "direct_reverse_dependencies": ["package-d"],
        "indirect_reverse_dependencies": ["package-b",
                                          "package-a"],
        "alternatives": {}
    }
    assert compare(dep_helper.get_package_details("package-e"), package_e_expected)


def test_package_f_details(status_content):
    dep_helper.build_graphs(status_content)
    package_f_expected = {
        "package": "package-f",
        "description": "Package F",
        "direct_dependencies": [],
        "indirect_dependencies": [],
        "direct_reverse_dependencies": [],
        "indirect_reverse_dependencies": [],
        "alternatives": {}
    }
    assert compare(dep_helper.get_package_details("package-f") , package_f_expected)


def test_packages_with_no_dependencies(status_content):
    dep_helper.build_graphs(status_content)
    no_deps_packages = dep_helper.get_packages_with_no_dependencies()
    assert "package-c" in no_deps_packages
    assert "package-e" in no_deps_packages
    assert "package-f" in no_deps_packages
