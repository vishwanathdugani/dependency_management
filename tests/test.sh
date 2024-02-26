#!/bin/bash

# Define the URL of your FastAPI application
HOST="http://localhost:8000"

# Specify the path to the status file you want to upload
STATUS_FILE_PATH="tests/status"
#
# Upload the status file
echo "Uploading status file..."
curl -X POST "${HOST}/upload-status-file/" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@${STATUS_FILE_PATH}"
echo -e "\n" # New line for readability

# List all packages
echo "Listing all packages..."
curl -X GET "${HOST}/packages/"
echo -e "\n" # New line for readability

# Define the package names to loop through
PACKAGES=("package-a" "package-b" "package-c" "package-d" "package-e" "package-f")

# Loop over each package and query for its details
for PACKAGE_NAME in "${PACKAGES[@]}"; do
    echo "Querying details for package: ${PACKAGE_NAME}..."
    curl -X GET "${HOST}/package/${PACKAGE_NAME}/"
    echo -e "\n" # New line for readability
done

# Query for packages with no dependencies after querying all packages
echo "Querying packages with no dependencies..."
curl -X GET "${HOST}/packages/no-dependencies/"
echo -e "\n" # New line for readability
