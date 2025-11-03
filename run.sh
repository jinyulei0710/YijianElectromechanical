#!/bin/bash
# 快速启动脚本 (macOS/Linux)

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在"
    echo "请先运行: ./setup.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查知识库
if [ ! -d "data/chroma_db" ]; then
    echo "⚠️  知识库未初始化"
    echo ""
    read -p "是否现在初始化知识库? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python init_knowledge_base.py
    else
        echo "请稍后运行: python init_knowledge_base.py"
        exit 1
    fi
fi

# 启动AI助手
python main.py

