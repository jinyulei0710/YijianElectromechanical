@echo off
REM 一建AI助手 - 自动化设置脚本 (Windows)

echo ======================================================================
echo 🎓 一建机电备考 AI 助手 - 自动化设置
echo ======================================================================
echo.

REM 检查 Python 是否安装
echo 📋 步骤 1/6: 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ 找到 Python %PYTHON_VERSION%

REM 创建虚拟环境
echo.
echo 📦 步骤 2/6: 创建虚拟环境...
if exist venv (
    echo ⚠️  虚拟环境已存在
    set /p RECREATE="是否删除并重新创建? (y/n): "
    if /i "%RECREATE%"=="y" (
        echo 删除旧的虚拟环境...
        rmdir /s /q venv
        python -m venv venv
        echo ✓ 虚拟环境已重新创建
    ) else (
        echo ✓ 使用现有虚拟环境
    )
) else (
    python -m venv venv
    echo ✓ 虚拟环境创建成功
)

REM 激活虚拟环境
echo.
echo 🔌 步骤 3/6: 激活虚拟环境...
call venv\Scripts\activate.bat
echo ✓ 虚拟环境已激活

REM 升级 pip
echo.
echo ⬆️  步骤 4/6: 升级 pip...
python -m pip install --upgrade pip -q
echo ✓ pip 已升级到最新版本

REM 安装依赖
echo.
echo 📚 步骤 5/6: 安装项目依赖...
echo 这可能需要几分钟时间...
pip install -r requirements.txt -q
echo ✓ 依赖安装完成

REM 配置环境变量
echo.
echo ⚙️  步骤 6/6: 配置环境变量...
if not exist .env (
    copy .env.example .env >nul
    echo ✓ 已创建 .env 文件
    echo.
    echo ⚠️  重要: 请编辑 .env 文件，设置你的 OPENAI_API_KEY
    echo    可以使用记事本或任何文本编辑器打开 .env 文件
) else (
    echo ✓ .env 文件已存在
)

REM 完成
echo.
echo ======================================================================
echo ✅ 设置完成！
echo ======================================================================
echo.
echo 📝 下一步操作:
echo.
echo 1. 配置 API 密钥（如果还没有）:
echo    notepad .env
echo.
echo 2. 测试系统:
echo    venv\Scripts\activate
echo    python test_system.py
echo.
echo 3. 初始化知识库:
echo    python init_knowledge_base.py
echo.
echo 4. 启动 AI 助手:
echo    python main.py
echo.
echo 💡 提示: 每次使用前需要激活虚拟环境:
echo    venv\Scripts\activate
echo.
echo ======================================================================
echo.
pause

