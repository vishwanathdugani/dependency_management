# Dependency management for Debian/Linux server packages

Dependency graph for status located in
/var/lib/dpkg/status that holds information about software packages.

This API utilizes a directed graph to manage package dependencies, where nodes represent packages, 
and edges denote dependencies. The API's core functionalities rely on depth-first search (DFS) for traversing the dependency graph. 



### Endpoints and How They Work

- **POST `/upload-status-file/`**: Accepts a multipart file upload containing package data. It parses the file to build dependency graphs for all listed packages. Example response: `{"message": "Graph built successfully"}` indicates successful graph construction. There is a start up task that load a sample status file. 
  
- **GET `/packages/`**: Lists all packages by their names and descriptions, providing a broad overview of the repository's contents.
  
- **GET `/package/{package_name}/`**: Offers detailed information about a specific package, including direct and indirect dependencies and reverse dependencies, showcasing the package's position within the ecosystem. In a dependency graph for managing Debian/Linux server packages, each node represents a package, and edges denote dependencies between them. The `"direct_dependencies"` are packages a given package immediately requires to function, while `"indirect_dependencies"` are those needed by its direct dependencies, extending further into the graph. `"Direct_reverse_dependencies"` are packages directly dependent on the given package, and `"indirect_reverse_dependencies"` extend this concept to include all packages reliant on those directly dependent packages. `"Alternatives"` offer optional dependencies that can substitute for the primary one, allowing flexibility in package selection and installation.
  
- **GET `/packages/no-dependencies/`**: Identifies packages that do not depend on others, highlighting potentially foundational or standalone components.


### API Documentation & Testing
Interactive Documentation: http://localhost:8000/docs (Swagger UI generated by FastAPI)


Running Tests:
`docker exec -it <container-name> pytest tests/tests.py`

This command executes tests in the container and generates a report named `report.html` in the tests directory.

There is a CI pipeline (github actions) that is implemented to automatically test the graph traversal and depenency retreival. 

### Repository and Docker Setup

To deploy the API locally using Docker, use the provided `docker-compose.yml` file with the `docker-compose up --build` command. 

### Future improvements and considerations
- The assumption was made that the user is trying to manage dependencies on a debian/ubuntu server where the file is stored. 
- API security with additional authentication and encryption layers.
- Develop a user interface for visual data representation, improving user experience.
- limited package information to name and description for better readability.
- Expand testing to thoroughly cover edge cases and ensure robustness.
- Transition from an in-memory model to a graph database for improved data management and scalability.
- Implement background async tasks for synchronization between the status file and graph database.
- Incorporate safeguards against circular dependencies to maintain system stability.