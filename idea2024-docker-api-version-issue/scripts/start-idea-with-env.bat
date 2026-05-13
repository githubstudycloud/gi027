@echo off
REM ============================================================
REM   Launch IDEA with DOCKER_API_VERSION injected (process-only).
REM   Does NOT modify global environment variables.
REM
REM   Usage:
REM     start-idea-with-env.bat
REM     start-idea-with-env.bat "C:\path\to\idea64.exe"
REM     start-idea-with-env.bat "C:\path\to\idea64.exe" 1.47
REM
REM   IDEA path resolution order:
REM     1) First CLI argument (%1)
REM     2) IDEA_PATH environment variable
REM     3) .idea-path.txt next to this bat (first non-comment line)
REM ============================================================

setlocal

REM --- API version (second arg or default) ---
if "%~2"=="" (
    set "DOCKER_API_VERSION=1.44"
) else (
    set "DOCKER_API_VERSION=%~2"
)

REM --- Resolve IDEA path ---
set "IDEA_EXE="

if not "%~1"=="" (
    set "IDEA_EXE=%~1"
    goto :have_path
)

if defined IDEA_PATH (
    set "IDEA_EXE=%IDEA_PATH%"
    goto :have_path
)

set "CFG=%~dp0.idea-path.txt"
if exist "%CFG%" (
    for /f "usebackq tokens=* delims=" %%L in ("%CFG%") do (
        set "_line=%%L"
        call :trim_and_set "%%L"
        if defined IDEA_EXE goto :have_path
    )
)

echo [ERROR] IDEA path not provided.
echo.
echo Provide it in any of these ways:
echo   1) Pass as first argument: start-idea-with-env.bat "C:\path\to\idea64.exe"
echo   2) Set env var IDEA_PATH and rerun.
echo   3) Copy .idea-path.txt.sample to .idea-path.txt and edit the path.
exit /b 1

:trim_and_set
set "_v=%~1"
if "%_v%"=="" goto :eof
if "%_v:~0,1%"=="#" goto :eof
set "IDEA_EXE=%_v%"
goto :eof

:have_path
if not exist "%IDEA_EXE%" (
    echo [ERROR] IDEA exe not found: %IDEA_EXE%
    exit /b 1
)

echo Launching: %IDEA_EXE%
echo   DOCKER_API_VERSION=%DOCKER_API_VERSION%
start "" "%IDEA_EXE%"
endlocal
