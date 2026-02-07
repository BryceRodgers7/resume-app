# Fix for local PyTorch installation
# This ensures your local environment matches the Fly.io production environment

Write-Host "Uninstalling existing PyTorch packages..." -ForegroundColor Yellow
pip uninstall -y torch torchvision

Write-Host "`nInstalling PyTorch CPU-only versions..." -ForegroundColor Yellow
pip install torch==2.0.0+cpu torchvision==0.15.0+cpu --index-url https://download.pytorch.org/whl/cpu

Write-Host "`nInstalling remaining requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`nDone! PyTorch CPU-only version installed successfully." -ForegroundColor Green
Write-Host "This matches your Fly.io production environment." -ForegroundColor Green
