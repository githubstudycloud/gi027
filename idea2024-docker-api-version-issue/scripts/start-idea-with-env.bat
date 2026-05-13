@echo off
REM ============================================================
REM   仅为本次启动的 IDEA 进程注入 DOCKER_API_VERSION
REM   不污染全局环境变量。
REM
REM   用法：
REM     1) 编辑下面的 IDEA_PATH 指向你的 idea64.exe
REM     2) 双击运行，或在快捷方式中使用此 bat
REM ============================================================

set DOCKER_API_VERSION=1.44

REM 修改为你的 IDEA 安装路径
set "IDEA_PATH=C:\Program Files\JetBrains\IntelliJ IDEA 2024.3\bin\idea64.exe"

if not exist "%IDEA_PATH%" (
    echo [ERROR] 未找到 IDEA: %IDEA_PATH%
    echo 请编辑本 bat 中的 IDEA_PATH 变量。
    pause
    exit /b 1
)

echo Starting IDEA with DOCKER_API_VERSION=%DOCKER_API_VERSION% ...
start "" "%IDEA_PATH%"
