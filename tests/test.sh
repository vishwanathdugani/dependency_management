#!/bin/bash

HOST="http://localhost:8000"

STATUS_FILE_PATH="tests/status"


echo "Uploading status file..."
curl -X POST "${HOST}/upload-status-file/" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@${STATUS_FILE_PATH}"
echo -e "\n"


echo "Listing all packages..."
curl -X GET "${HOST}/packages/"
echo -e "\n"

PACKAGES=("package-a" "package-b" "package-c" "package-d" "package-e" "package-f")

for PACKAGE_NAME in "${PACKAGES[@]}"; do
    echo "Querying details for package: ${PACKAGE_NAME}..."
    curl -X GET "${HOST}/package/${PACKAGE_NAME}/"
    echo -e "\n"
done

echo "Querying packages with no dependencies..."
curl -X GET "${HOST}/packages/no-dependencies/"
echo -e "\n"
