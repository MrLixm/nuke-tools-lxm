@echo off

set THISDIR=%~dp0

set "NUKE_PATH=%THISDIR%"
set "PYTHONPATH=%THISDIR%..\"

start "" "C:\Program Files\Nuke15.1v2\Nuke15.1.exe" --nukex --nc %THISDIR%\test-scene-1.nknc