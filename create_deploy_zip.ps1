$deployDir = New-Item -ItemType Directory -Path "deploy_temp" -Force
Copy-Item -Path "api\*" -Destination $deployDir -Recurse -Force
Copy-Item -Path "marketing_warehouse.db" -Destination $deployDir -Force
Copy-Item -Path "requirements.txt" -Destination $deployDir -Force
$zipPath = "deploy.zip"
Compress-Archive -Path "$deployDir\*" -DestinationPath $zipPath -Force
Write-Output (Resolve-Path $zipPath).Path
