#!/bin/bash

echo "========================================"
echo "Building AI File Finder MVP"
echo "========================================"

# Step 1: Build Python Backend
echo -e "\n[1/4] Building Python Backend..."
cd backend

# Activate virtual environment
source venv/bin/activate

# Install PyInstaller
pip install pyinstaller

# Build backend
pyinstaller build_backend.spec --clean

if [ $? -ne 0 ]; then
    echo "Backend build failed!"
    exit 1
fi

# Step 2: Copy backend to frontend
echo -e "\n[2/4] Copying backend to frontend..."
rm -rf ../frontend/backend-dist
cp -r dist/AIFileFinderBackend ../frontend/backend-dist
echo "Backend copied to frontend/backend-dist"

cd ..

# Step 3: Build Frontend
echo -e "\n[3/4] Building Frontend..."
cd frontend

npm install
npm run build

if [ $? -ne 0 ]; then
    echo "Frontend build failed!"
    exit 1
fi

# Step 4: Build Tauri App
echo -e "\n[4/4] Building Tauri Application..."
npm run tauri build

if [ $? -ne 0 ]; then
    echo "Tauri build failed!"
    exit 1
fi

cd ..

echo -e "\n========================================"
echo "Build Complete!"
echo "========================================"
echo -e "\nInstaller location:"
echo "frontend/src-tauri/target/release/bundle/dmg/"
echo -e "\nOr portable:"
echo "frontend/src-tauri/target/release/AI File Finder"