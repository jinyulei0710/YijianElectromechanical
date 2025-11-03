"""
系统测试脚本
用于验证各个模块是否正常工作
"""

import sys
from pathlib import Path


def test_imports():
    """测试依赖库导入"""
    print("=" * 60)
    print("测试 1/4: 检查依赖库")
    print("=" * 60)
    
    required_modules = [
        ('pdfplumber', 'PDF解析'),
        ('chromadb', '向量数据库'),
        ('openai', 'OpenAI客户端'),
        ('dotenv', '环境变量管理'),
    ]
    
    all_ok = True
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"✓ {description} ({module_name})")
        except ImportError:
            print(f"✗ {description} ({module_name}) - 未安装")
            all_ok = False
    
    return all_ok


def test_pdf_files():
    """测试PDF文件是否存在"""
    print("\n" + "=" * 60)
    print("测试 2/4: 检查PDF教材文件")
    print("=" * 60)
    
    # 使用当前目录作为基础路径
    base_path = Path(".")
    pdf_files = [
        ("工程经济", base_path / "工程经济" / "2025年一建经济电子版教材.pdf"),
        ("机电实务", base_path / "机电实务" / "2025年一建机电电子版教材.pdf"),
        ("法律法规", base_path / "法律法规" / "2025年一建法规电子版教材.pdf"),
        ("项目管理", base_path / "项目管理" / "2025年一建管理电子版教材.pdf"),
    ]
    
    all_ok = True
    for subject, pdf_path in pdf_files:
        if pdf_path.exists():
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"✓ {subject}: {pdf_path.name} ({size_mb:.1f} MB)")
        else:
            print(f"✗ {subject}: 文件不存在 - {pdf_path}")
            all_ok = False
    
    return all_ok


def test_env_config():
    """测试环境配置"""
    print("\n" + "=" * 60)
    print("测试 3/4: 检查环境配置")
    print("=" * 60)
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("✗ .env 文件不存在")
        print("  请运行: cp .env .env")
        print("  然后编辑 .env 文件，设置 OPENAI_API_KEY")
        return False
    
    print("✓ .env 文件存在")
    
    # 检查API密钥
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("✗ OPENAI_API_KEY 未设置")
        return False
    
    if api_key == "your_openai_api_key_here":
        print("✗ OPENAI_API_KEY 未修改（仍是默认值）")
        return False
    
    print(f"✓ OPENAI_API_KEY 已设置 ({api_key[:10]}...)")
    
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    print(f"✓ OPENAI_BASE_URL: {base_url}")
    
    return True


def test_knowledge_base():
    """测试知识库"""
    print("\n" + "=" * 60)
    print("测试 4/4: 检查知识库")
    print("=" * 60)
    
    kb_path = Path("./data/chroma_db")
    
    if not kb_path.exists():
        print("✗ 知识库未初始化")
        print("  请运行: python init_knowledge_base.py")
        return False
    
    print("✓ 知识库目录存在")
    
    try:
        from knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        stats = kb.get_stats()
        
        if stats['total'] == 0:
            print("✗ 知识库为空")
            print("  请运行: python init_knowledge_base.py")
            return False
        
        print(f"✓ 知识库包含 {stats['total']} 条记录")
        
        if stats['by_subject']:
            print("\n  各科目统计:")
            for subject, count in stats['by_subject'].items():
                print(f"    - {subject}: {count}")
        
        return True
        
    except Exception as e:
        print(f"✗ 知识库检查失败: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("\n🔍 一建AI助手系统测试\n")
    
    results = []
    
    # 运行所有测试
    results.append(("依赖库", test_imports()))
    results.append(("PDF文件", test_pdf_files()))
    results.append(("环境配置", test_env_config()))
    results.append(("知识库", test_knowledge_base()))
    
    # 显示总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 所有测试通过！系统已准备就绪。")
        print("\n现在可以运行:")
        print("  python main.py")
        print("或")
        print("  python ai_agent.py")
    else:
        print("⚠️  部分测试失败，请根据上述提示解决问题。")
        print("\n快速修复步骤:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 配置环境: cp .env .env (然后编辑.env)")
        print("3. 初始化知识库: python init_knowledge_base.py")
    
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

