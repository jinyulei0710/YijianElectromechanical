"""
主程序入口
启动一建备考AI助手
"""

import sys
from pathlib import Path
from ai_agent import YijianAIAgent
from knowledge_base import KnowledgeBase


def check_environment():
    """检查运行环境"""
    issues = []
    
    # 检查.env文件
    env_file = Path(".env")
    if not env_file.exists():
        issues.append("❌ 未找到.env文件，请复制.env.example并配置OPENAI_API_KEY")
    
    # 检查知识库
    kb_path = Path("./data/chroma_db")
    if not kb_path.exists():
        issues.append("❌ 知识库未初始化，请先运行: python init_knowledge_base.py")
    else:
        # 检查知识库是否有数据
        try:
            kb = KnowledgeBase()
            stats = kb.get_stats()
            if stats['total'] == 0:
                issues.append("❌ 知识库为空，请运行: python init_knowledge_base.py")
        except Exception as e:
            issues.append(f"❌ 知识库检查失败: {str(e)}")
    
    return issues


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🎓 一建机电备考 AI 助手")
    print("=" * 60 + "\n")
    
    # 检查环境
    print("🔍 检查运行环境...")
    issues = check_environment()
    
    if issues:
        print("\n⚠️  发现以下问题:\n")
        for issue in issues:
            print(f"   {issue}")
        print("\n请解决上述问题后再运行程序。")
        print("\n💡 快速开始:")
        print("   1. 复制配置文件: cp .env .env")
        print("   2. 编辑.env文件，填入你的OPENAI_API_KEY")
        print("   3. 初始化知识库: python init_knowledge_base.py")
        print("   4. 启动助手: python main.py")
        sys.exit(1)
    
    print("✓ 环境检查通过\n")
    
    # 启动AI助手
    try:
        agent = YijianAIAgent()
        agent.chat()
    except KeyboardInterrupt:
        print("\n\n👋 再见！祝你考试顺利！")
    except Exception as e:
        print(f"\n❌ 启动失败: {str(e)}")
        print("\n请检查:")
        print("1. 依赖是否已安装: pip install -r requirements.txt")
        print("2. .env文件中的API配置是否正确")
        print("3. 知识库是否已正确初始化")
        sys.exit(1)


if __name__ == "__main__":
    main()

