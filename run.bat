@echo off
REM 快速启动脚本 (Windows)

REM 检查虚拟环境是否存在
if not exist venv (
    echo ❌ 虚拟环境不存在
    echo 请先运行: setup.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查知识库
if not exist data\chroma_db (
    echo ⚠️  知识库未初始化
    echo.
    set /p INIT="是否现在初始化知识库? (y/n): "
    if /i "%INIT%"=="y" (
        python init_knowledge_base.py
    ) else (
        echo 请稍后运行: python init_knowledge_base.py
        pause
        exit /b 1
    )
)

REM 启动AI助手
python main.py
pause

