param([Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference='Stop'
if (-not $env:DATABASE_URL) { throw 'Set DATABASE_URL first' }
& pg_dump --dbname=$env:DATABASE_URL --format=custom --no-owner --no-acl --file=$Destination
if ($LASTEXITCODE -ne 0) { throw 'Backup failed' }
Get-FileHash -Algorithm SHA256 -LiteralPath $Destination
