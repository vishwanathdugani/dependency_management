from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from graph_functions.dependencies_helper import DependenciesHelper
from graph_functions.schemas import PackageResponseModel, PackageDetailsModel

app = FastAPI()
dep_helper = DependenciesHelper()

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-Requested-With", "Content-Type"],
)


@app.post("/upload-status-file/")
async def upload_status_file(file: UploadFile = File(...)):
    """
    Uploads a status file and builds the dependency graphs based on its content.
    """
    content_bytes = await file.read()
    content_str = content_bytes.decode('utf-8')
    dep_helper.build_graphs(content_str)
    return [
        {
            "package": pkg,
        }
        for pkg, info in dep_helper.dependencies_graph.items()
    ]


@app.get("/packages/", response_model=List[PackageResponseModel])
def list_packages():
    """
    Lists all packages with their descriptions.
    """
    return [
        {
            "package": pkg,
            "description": info.Description,
            "priority": info.Priority,
            "status": info.Status,
            "version": info.Version,
            "architecture": info.Architecture,
            "installed": info.Installed,
         }
        for pkg, info in dep_helper.dependencies_graph.items()
    ]


@app.get("/package/{package_name}/", response_model=PackageDetailsModel)
def package_details(package_name: str, request: Request):
    """
    Retrieves detailed information about a specific package.
    """
    # base_url = str(request.base_url).rstrip('/')
    package_info = dep_helper.get_package_details(package_name)
    if not package_info:
        raise HTTPException(status_code=404, detail="Package not found")
    return package_info


@app.get("/packages/no-dependencies/")
def packages_with_no_dependencies():
    """
    Lists packages that have no dependencies.
    """
    packages = dep_helper.get_packages_with_no_dependencies()
    if not packages:
        return {"message": "All packages have dependencies"}
    return {"packages": packages}


@app.on_event("startup")
async def startup_event():
    status_file_path = Path('status')
    if status_file_path.exists():
        content_str = status_file_path.read_text()
        dep_helper.build_graphs(content_str)
