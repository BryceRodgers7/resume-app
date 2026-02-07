#!/bin/bash
# Fix for local PyTorch installation
# This ensures your local environment matches the Fly.io production environment

echo "Uninstalling existing PyTorch packages..."
pip uninstall -y torch torchvision

echo ""
echo "Installing PyTorch CPU-only versions..."
pip install torch==2.0.0+cpu torchvision==0.15.0+cpu --index-url https://download.pytorch.org/whl/cpu

echo ""
echo "Installing remaining requirements..."
pip install -r requirements.txt

echo ""
echo "Done! PyTorch CPU-only version installed successfully."
echo "This matches your Fly.io production environment."
