Write-Host "Syncing dependencies with uv..."
uv sync
Write-Host "If needed, copy .env.example to .env and review provider settings."
Write-Host "Bootstrap complete."
