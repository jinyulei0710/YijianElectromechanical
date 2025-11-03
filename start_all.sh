#!/bin/bash

echo "============================================================"
echo "🚀 启动一建机电备考 AI 助手"
echo "============================================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 setup.sh"
    exit 1
fi

# 检查知识库
if [ ! -d "data/chroma_db" ]; then
    echo "❌ 知识库未初始化，请先运行: python init_knowledge_base.py"
    exit 1
fi

# 检查前端目录
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ 前端依赖未安装，请先运行: cd frontend && npm install"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 启动后端
echo "🔧 启动后端 API 服务器..."
source venv/bin/activate
python api_server.py &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"
echo "   后端地址: http://localhost:5001"
echo ""

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端开发服务器..."
cd frontend
source ~/.nvm/nvm.sh
nvm use 22 > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!
cd ..
echo "   前端 PID: $FRONTEND_PID"
echo "   前端地址: http://localhost:5173"
echo ""

echo "============================================================"
echo "✅ 所有服务已启动"
echo "============================================================"
echo ""
echo "📱 访问应用:"
echo "   前端界面: http://localhost:5173"
echo "   后端 API: http://localhost:5001"
echo ""
echo "💡 提示:"
echo "   - 在浏览器中打开 http://localhost:5173 使用应用"
echo "   - 按 Ctrl+C 停止所有服务"
echo ""
echo "============================================================"

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止所有服务..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ 所有服务已停止"
    exit 0
}

# 捕获中断信号
trap cleanup INT TERM

# 等待
wait

