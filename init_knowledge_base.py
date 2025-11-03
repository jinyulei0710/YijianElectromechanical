"""
知识库初始化脚本
解析所有PDF教材并构建知识库
"""

import sys
from pathlib import Path
from pdf_parser import parse_all_pdfs
from knowledge_base import KnowledgeBase


def init_knowledge_base(reset: bool = False):
    """
    初始化知识库
    
    Args:
        reset: 是否重置现有知识库
    """
    print("=" * 60)
    print("🚀 一建教材知识库初始化")
    print("=" * 60)
    
    # 1. 初始化知识库
    print("\n📦 步骤 1/3: 初始化知识库...")
    kb = KnowledgeBase()
    
    # 如果需要重置
    if reset:
        print("⚠️  重置现有知识库...")
        kb.reset()
    
    # 检查是否已有数据
    stats = kb.get_stats()
    if stats['total'] > 0 and not reset:
        print(f"\n✓ 知识库已存在，包含 {stats['total']} 条记录")
        print("\n如需重新初始化，请运行: python init_knowledge_base.py --reset")
        return
    
    # 2. 解析PDF教材
    print("\n📚 步骤 2/3: 解析PDF教材...")
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    try:
        documents = parse_all_pdfs()
        
        if not documents:
            print("\n❌ 错误：没有解析到任何文档")
            print("请检查PDF文件是否存在于以下目录：")
            print("  - Desktop/kaoLong/工程经济/")
            print("  - Desktop/kaoLong/机电实务/")
            print("  - Desktop/kaoLong/法律法规/")
            print("  - Desktop/kaoLong/项目管理/")
            return
        
        print(f"\n✓ 成功解析 {len(documents)} 个文本块")
        
    except Exception as e:
        print(f"\n❌ 解析PDF时出错: {str(e)}")
        return
    
    # 3. 添加到知识库
    print("\n💾 步骤 3/3: 构建向量数据库...")
    
    try:
        kb.add_documents(documents)
        
        # 显示最终统计
        final_stats = kb.get_stats()
        print("\n" + "=" * 60)
        print("✅ 知识库初始化完成！")
        print("=" * 60)
        print(f"\n📊 统计信息:")
        print(f"   总文档数: {final_stats['total']}")
        if final_stats['by_subject']:
            print("   各科目文档数:")
            for subject, count in final_stats['by_subject'].items():
                print(f"   - {subject}: {count}")
        
        print("\n🎉 现在可以运行 'python main.py' 或 'python ai_agent.py' 开始使用AI助手！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 构建知识库时出错: {str(e)}")
        return


if __name__ == "__main__":
    # 检查是否需要重置
    reset = "--reset" in sys.argv or "-r" in sys.argv
    
    if reset:
        confirm = input("⚠️  确定要重置知识库吗？这将删除所有现有数据。(yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("已取消")
            sys.exit(0)
    
    init_knowledge_base(reset=reset)

