#!/bin/bash

# 一建机电备考系统 - 真题系统启动脚本

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║              🎓 一建机电备考系统 - 真题系统启动                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 未找到Python虚拟环境，请先运行 setup.sh"
    exit 1
fi

# 检查Node.js版本
echo "🔍 检查Node.js版本..."
source ~/.nvm/nvm.sh
CURRENT_NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)

if [ "$CURRENT_NODE_VERSION" -lt 20 ]; then
    echo "⚠️  当前Node.js版本过低，切换到v22.21.1..."
    nvm use 22.21.1
    if [ $? -ne 0 ]; then
        echo "❌ 切换Node.js版本失败，请手动运行: nvm use 22.21.1"
        exit 1
    fi
fi

echo "✅ Node.js版本: $(node -v)"
echo ""

# 检查数据库
if [ ! -f "data/exam_questions.db" ]; then
    echo "⚠️  未找到真题数据库，正在构建..."
    source venv/bin/activate
    python3 exam_database.py
    if [ $? -ne 0 ]; then
        echo "❌ 数据库构建失败"
        exit 1
    fi
    echo ""
fi

# 启动后端API服务器
echo "🚀 启动后端API服务器..."
source venv/bin/activate
python3 api_server.py &
API_PID=$!
echo "✅ 后端API服务器已启动 (PID: $API_PID)"
echo "   地址: http://localhost:5001"
echo ""

# 等待API服务器启动
sleep 3

# 启动前端开发服务器
echo "🚀 启动前端开发服务器..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端开发服务器已启动 (PID: $FRONTEND_PID)"
echo "   地址: http://localhost:5173"
echo ""

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                          ✅ 系统启动成功！                                    ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📡 后端API服务器: http://localhost:5001"
echo "🌐 前端界面:      http://localhost:5173"
echo ""
echo "💡 使用说明:"
echo "   1. 打开浏览器访问 http://localhost:5173"
echo "   2. 点击顶部'📝 历年真题'标签查看真题"
echo "   3. 点击'💬 AI问答'标签使用AI助手"
echo ""
echo "🛑 停止服务:"
echo "   按 Ctrl+C 停止所有服务"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "按 Ctrl+C 停止所有服务..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $API_PID $FRONTEND_PID 2>/dev/null; echo '✅ 所有服务已停止'; exit 0" INT

# 保持脚本运行
wait

