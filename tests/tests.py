import pytest
from graph_functions.dependencies_helper import build_graphs, get_package_details, get_packages_with_no_dependencies


# Load the status file for testing
@pytest.fixture(scope="module")
def load_status():
    with open("tests/status", "r") as file:
        content = file.read()
    return content


# Test building graphs from the status file
def test_build_graphs(load_status):
    build_graphs(load_status)
    from graph_functions.dependencies_helper import dependencies_graph
    assert "package-a" in dependencies_graph
    assert "package-e" in dependencies_graph
    assert dependencies_graph["package-a"].Depends == {"package-b"}


def test_get_package_details_direct_and_indirect(load_status):
    base_url = "http://localhost:8000"
    build_graphs(load_status)
    package_details_a = get_package_details("package-a", base_url)

    # Form the expected URLs for direct and indirect dependencies
    expected_direct_deps_urls = {f"{base_url}/package/package-b"}
    expected_indirect_deps_urls = {f"{base_url}/package/package-c", f"{base_url}/package/package-d", f"{base_url}/package/package-e"}

    # Extract the actual URLs from the package details
    actual_direct_deps_urls = set(package_details_a["direct_dependencies"])
    actual_indirect_deps_urls = set(package_details_a["indirect_dependencies"])

    # Assertions to check if the actual URLs match the expected URLs
    assert actual_direct_deps_urls == expected_direct_deps_urls, "Direct dependencies URLs do not match the expected values."
    assert actual_indirect_deps_urls == expected_indirect_deps_urls, "Indirect dependencies URLs do not match the expected values."

    # Optionally, for more detailed assertion messages, you can check for the presence of each expected URL
    for expected_url in expected_direct_deps_urls:
        assert expected_url in actual_direct_deps_urls, f"Expected direct dependency URL '{expected_url}' not found in actual direct dependencies URLs."

    for expected_url in expected_indirect_deps_urls:
        assert expected_url in actual_indirect_deps_urls, f"Expected indirect dependency URL '{expected_url}' not found in actual indirect dependencies URLs."


# Test package with no dependencies
def test_package_no_dependencies(load_status):
    build_graphs(load_status)
    package_details_e = get_package_details("package-e", "http://localhost:8000")
    assert not package_details_e["direct_dependencies"]
    assert not package_details_e["indirect_dependencies"]



def test_calculate_installation_sequence(load_status):
    build_graphs(load_status)
    sequence = calculate_installation_sequence()
    assert sequence.index("package-b") > sequence.index("package-c")
    assert sequence.index("package-b") > sequence.index("package-d")

def test_packages_with_no_dependencies(load_status):
    build_graphs(load_status)
    no_deps = get_packages_with_no_dependencies()
    # package-c and package-e have no dependencies in the sample
    assert "package-c" in no_deps
    assert "package-e" in no_deps
    assert "package-a" not in no_deps  # Has dependencies