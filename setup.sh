#!/bin/bash
# 一建AI助手 - 自动化设置脚本 (macOS/Linux)

set -e  # 遇到错误立即退出

echo "======================================================================"
echo "🎓 一建机电备考 AI 助手 - 自动化设置"
echo "======================================================================"
echo ""

# 检查 Python 是否安装
echo "📋 步骤 1/6: 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ 错误: 未找到 Python"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✓ 找到 Python $PYTHON_VERSION"

# 创建虚拟环境
echo ""
echo "📦 步骤 2/6: 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在"
    read -p "是否删除并重新创建? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除旧的虚拟环境..."
        rm -rf venv
        $PYTHON_CMD -m venv venv
        echo "✓ 虚拟环境已重新创建"
    else
        echo "✓ 使用现有虚拟环境"
    fi
else
    $PYTHON_CMD -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo ""
echo "🔌 步骤 3/6: 激活虚拟环境..."
source venv/bin/activate
echo "✓ 虚拟环境已激活"

# 升级 pip
echo ""
echo "⬆️  步骤 4/6: 升级 pip..."
pip install --upgrade pip -q
echo "✓ pip 已升级到最新版本"

# 安装依赖
echo ""
echo "📚 步骤 5/6: 安装项目依赖..."
echo "这可能需要几分钟时间..."
pip install -r requirements.txt -q
echo "✓ 依赖安装完成"

# 配置环境变量
echo ""
echo "⚙️  步骤 6/6: 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ 已创建 .env 文件"
    echo ""
    echo "⚠️  重要: 请编辑 .env 文件，设置你的 OPENAI_API_KEY"
    echo "   可以使用以下命令编辑:"
    echo "   nano .env"
    echo "   或"
    echo "   vim .env"
    echo "   或使用任何文本编辑器"
else
    echo "✓ .env 文件已存在"
fi

# 完成
echo ""
echo "======================================================================"
echo "✅ 设置完成！"
echo "======================================================================"
echo ""
echo "📝 下一步操作:"
echo ""
echo "1. 配置 API 密钥（如果还没有）:"
echo "   nano .env"
echo ""
echo "2. 测试系统:"
echo "   source venv/bin/activate"
echo "   python test_system.py"
echo ""
echo "3. 初始化知识库:"
echo "   python init_knowledge_base.py"
echo ""
echo "4. 启动 AI 助手:"
echo "   python main.py"
echo ""
echo "💡 提示: 每次使用前需要激活虚拟环境:"
echo "   source venv/bin/activate"
echo ""
echo "======================================================================"

