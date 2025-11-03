"""
AI Agent核心模块
基于知识库实现智能问答功能
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from knowledge_base import KnowledgeBase

# 加载环境变量
load_dotenv()


class YijianAIAgent:
    """一建备考AI助手"""
    
    def __init__(self, knowledge_base: KnowledgeBase = None):
        """
        初始化AI Agent
        
        Args:
            knowledge_base: 知识库实例
        """
        # 初始化知识库
        self.kb = knowledge_base or KnowledgeBase()
        
        # 初始化OpenAI客户端
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not api_key:
            raise ValueError("请在.env文件中设置OPENAI_API_KEY")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        # 模型名称（支持环境变量配置）
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # 系统提示词
        self.system_prompt = """你是一个专业的一级建造师考试辅导助手。你的任务是帮助考生理解和掌握一建考试的知识点。

你的特点：
1. 专业：精通工程经济、机电实务、法律法规、项目管理四个科目
2. 耐心：用通俗易懂的语言解释复杂概念
3. 准确：基于官方教材内容回答问题，不编造信息
4. 实用：结合实际案例帮助理解，提供记忆技巧

回答要求：
- 基于提供的教材内容回答问题
- 如果教材中没有相关内容，请明确说明
- 适当使用要点、编号等格式使答案更清晰
- 可以补充相关知识点帮助理解
- 如果问题涉及多个科目，请分别说明
"""
    
    def answer(self, question: str, subject_filter: str = None, n_context: int = 5) -> str:
        """
        回答问题
        
        Args:
            question: 用户问题
            subject_filter: 科目过滤（可选）
            n_context: 检索的上下文数量
            
        Returns:
            AI的回答
        """
        # 1. 从知识库检索相关内容
        print("🔍 正在检索相关知识...")
        contexts = self.kb.search(question, n_results=n_context, subject_filter=subject_filter)
        
        if not contexts:
            return "抱歉，我在教材中没有找到相关内容。请尝试换个方式提问，或者确认知识库已正确初始化。"
        
        # 2. 构建上下文
        context_text = self._build_context(contexts)
        
        # 3. 构建提示词
        user_prompt = f"""基于以下教材内容回答问题。

【教材内容】
{context_text}

【问题】
{question}

请基于上述教材内容给出专业、准确的回答。如果教材内容不足以完整回答问题，请说明并给出你能提供的信息。
"""
        
        # 4. 调用LLM生成回答
        print("🤖 AI正在思考...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            
            # 5. 添加引用信息
            sources = self._format_sources(contexts)
            full_answer = f"{answer}\n\n{sources}"
            
            return full_answer
            
        except Exception as e:
            return f"抱歉，生成回答时出错: {str(e)}\n请检查API配置是否正确。"
    
    def _build_context(self, contexts: List[Dict[str, any]]) -> str:
        """
        构建上下文文本
        
        Args:
            contexts: 检索到的上下文列表
            
        Returns:
            格式化的上下文文本
        """
        context_parts = []
        
        for i, ctx in enumerate(contexts, 1):
            metadata = ctx['metadata']
            text = ctx['text']
            
            context_parts.append(
                f"[片段{i}] 来源：{metadata['subject']} - {metadata['source']} (第{metadata['page']}页)\n{text}"
            )
        
        return "\n\n".join(context_parts)
    
    def _format_sources(self, contexts: List[Dict[str, any]]) -> str:
        """
        格式化引用来源
        
        Args:
            contexts: 上下文列表
            
        Returns:
            格式化的来源信息
        """
        sources = []
        seen = set()
        
        for ctx in contexts:
            metadata = ctx['metadata']
            source_key = f"{metadata['subject']}-{metadata['page']}"
            
            if source_key not in seen:
                sources.append(f"- {metadata['subject']} 第{metadata['page']}页")
                seen.add(source_key)
        
        if sources:
            return "📚 **参考来源：**\n" + "\n".join(sources)
        return ""
    
    def chat(self):
        """
        启动交互式对话
        """
        print("=" * 60)
        print("🎓 一建机电备考 AI 助手")
        print("=" * 60)
        
        # 显示知识库统计
        stats = self.kb.get_stats()
        print(f"\n📊 知识库状态:")
        print(f"   总文档数: {stats['total']}")
        if stats['by_subject']:
            print("   各科目:")
            for subject, count in stats['by_subject'].items():
                print(f"   - {subject}: {count} 个文本块")
        
        print("\n💡 使用提示:")
        print("   - 直接输入问题，AI会基于教材内容回答")
        print("   - 输入 'exit' 或 'quit' 退出")
        print("   - 输入 'help' 查看帮助")
        print("   - 输入 'stats' 查看知识库统计")
        print("\n" + "=" * 60 + "\n")
        
        while True:
            try:
                # 获取用户输入
                question = input("🙋 你的问题: ").strip()
                
                if not question:
                    continue
                
                # 处理特殊命令
                if question.lower() in ['exit', 'quit', '退出']:
                    print("\n👋 再见！祝你考试顺利！")
                    break
                
                if question.lower() == 'help':
                    self._show_help()
                    continue
                
                if question.lower() == 'stats':
                    self._show_stats()
                    continue
                
                # 回答问题
                print()
                answer = self.answer(question)
                print(f"\n💬 AI回答:\n{answer}\n")
                print("-" * 60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！祝你考试顺利！")
                break
            except Exception as e:
                print(f"\n❌ 出错了: {str(e)}\n")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n📖 帮助信息:")
        print("   1. 直接提问：输入你的问题，AI会基于教材回答")
        print("   2. 示例问题：")
        print("      - 什么是工程造价？")
        print("      - 机电工程的施工流程是什么？")
        print("      - 建设工程法律法规有哪些？")
        print("      - 项目管理的主要内容是什么？")
        print("   3. 特殊命令：")
        print("      - stats: 查看知识库统计")
        print("      - help: 显示此帮助")
        print("      - exit/quit: 退出程序")
        print()
    
    def _show_stats(self):
        """显示统计信息"""
        stats = self.kb.get_stats()
        print(f"\n📊 知识库统计:")
        print(f"   总文档数: {stats['total']}")
        if stats['by_subject']:
            print("   各科目文档数:")
            for subject, count in stats['by_subject'].items():
                print(f"   - {subject}: {count}")
        print()


if __name__ == "__main__":
    # 启动AI助手
    try:
        agent = YijianAIAgent()
        agent.chat()
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        print("请确保:")
        print("1. 已安装所有依赖: pip install -r requirements.txt")
        print("2. 已配置.env文件并设置OPENAI_API_KEY")
        print("3. 已运行 python init_knowledge_base.py 初始化知识库")

