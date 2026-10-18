param([ValidateSet('serve','analyze','doctor')][string]$Mode='serve',[string]$Pdf='',[string]$Output='')
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
$taskPython=Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) { throw '请先按 README 创建 .venv 并安装依赖。' }
if ($Mode -eq 'analyze') {
    if (-not $Pdf) { throw '请提供 -Pdf 文件路径。' }
    if (-not $Output) { $Output=Join-Path $PSScriptRoot 'outputs\paper' }
    & $taskPython -m paperweave analyze $Pdf -o $Output
} else { & $taskPython -m paperweave $Mode }
exit $LASTEXITCODE
