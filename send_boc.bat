@echo off
setlocal
set "REPO=%~dp0"
python "%REPO%implementations\korg\ms2000\tools\send_to_ms2000.py" --out 6 --file "%REPO%implementations\korg\ms2000\patches\BOCPatches.syx"
endlocal

