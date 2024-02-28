import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from graph_functions.dependencies_helper import build_graphs, get_package_details, get_packages_with_no_dependencies
from typing import List

from graph_functions.schemas import PackageResponseModel, PackageDetailsModel

app = FastAPI()


@app.post("/upload-status-file/")
async def upload_status_file(file: UploadFile = File(...)):
    """
    Uploads a status file and builds the dependency graphs based on its content.
    """
    content_bytes = await file.read()
    content_str = content_bytes.decode('utf-8')
    build_graphs(content_str)
    return {"message": "Graph built successfully"}


@app.get("/packages/", response_model=List[PackageResponseModel])
def list_packages():
    """
    Lists all packages with their descriptions.
    """
    from graph_functions.dependencies_helper import dependencies_graph
    return [
        {"package": pkg, "description": info.Description}
        for pkg, info in dependencies_graph.items()
    ]


@app.get("/package/{package_name}/", response_model=PackageDetailsModel)
def package_details(package_name: str, request: Request):
    """
    Retrieves detailed information about a specific package.
    """
    base_url = str(request.base_url).rstrip('/')
    package_info = get_package_details(package_name, base_url)
    if not package_info:
        raise HTTPException(status_code=404, detail="Package not found")
    return package_info


@app.get("/packages/no-dependencies/")
def packages_with_no_dependencies():
    """
    Lists packages that have no dependencies.
    """
    packages = get_packages_with_no_dependencies()
    if not packages:
        return {"message": "All packages have dependencies"}
    return {"packages": packages}


@app.on_event("startup")
async def startup_event():
    status_file_path = 'status'
    if os.path.exists(status_file_path):
        with open(status_file_path, 'r') as file:
            content_str = file.read()
            build_graphs(content_str)
