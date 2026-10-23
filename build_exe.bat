
@echo off
REM ============================================================================
REM build_exe.bat  -  baut SystemLab.exe und packt sie als ZIP fuer Testpersonen
REM Doppelklick genuegt. Ergebnis: dist\SystemLab_Beta.zip
REM ============================================================================
cd /d "%~dp0"

REM Python, mit dem die Bau-Umgebung erstellt wird
set CONDA_ENV=C:\Anaconda3Envs\eh-rd-all-in-one
set BASIS_PY=%CONDA_ENV%\python.exe

REM Anaconda-DLLs (tk86t.dll, ffi-8.dll, libssl ...) fuer PyInstaller auffindbar machen
set PATH=%CONDA_ENV%\Library\bin;%CONDA_ENV%\DLLs;%PATH%

REM Bau-Umgebung + EXE ausserhalb von OneDrive (OneDrive sperrt sonst Dateien)
set BAU=%LOCALAPPDATA%\SystemLab_build
set ENV_PY=%BAU%\env\Scripts\python.exe

echo [1/3] Bau-Umgebung pruefen - beim ersten Mal dauert es etwas ...
"%BASIS_PY%" -m venv "%BAU%\env" || goto fehler
"%ENV_PY%" -m pip install -q --disable-pip-version-check -r requirements.txt pyinstaller || goto fehler

echo [2/3] Baue SystemLab.exe ...
"%ENV_PY%" -m PyInstaller SystemLab.spec --noconfirm --clean --log-level WARN --workpath "%BAU%\work" --distpath "%BAU%\dist" || goto fehler

echo [3/3] Packe ZIP ...
if not exist dist mkdir dist
del /q "dist\SystemLab_Beta.zip" 2>nul
tar -a -c -f "dist\SystemLab_Beta.zip" -C "%BAU%\dist" SystemLab || goto fehler

echo.
echo FERTIG:  dist\SystemLab_Beta.zip
echo Test-EXE: %BAU%\dist\SystemLab\SystemLab.exe
pause
exit /b 0

:fehler
echo.
echo FEHLER beim Bauen - Meldung oben lesen.
pause
exit /b 1