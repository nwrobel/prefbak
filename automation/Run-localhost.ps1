$projectDir = (Join-Path $PSScriptRoot -ChildPath '..')
$projectMainFilepath = (Join-Path $projectDir -ChildPath 'main.py')

& (Join-Path $projectDir -ChildPath 'py-venv-windows\Scripts\Activate.ps1')
python $projectMainFilepath hostname.config.json --run-all