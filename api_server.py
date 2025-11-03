"""
Flask API 服务器
提供 HTTP 接口供前端调用
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from ai_agent import YijianAIAgent
from knowledge_base import KnowledgeBase
from exam_database import ExamDatabase
import traceback

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)

# 配置 CORS（允许前端跨域访问）
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 全局变量：AI Agent 实例
ai_agent = None
knowledge_base = None
exam_db = None


def init_services():
    """初始化服务"""
    global ai_agent, knowledge_base, exam_db

    try:
        # 初始化知识库
        print("🔍 正在加载知识库...")
        knowledge_base = KnowledgeBase()

        # 初始化 AI Agent
        print("🤖 正在初始化 AI Agent...")
        ai_agent = YijianAIAgent(knowledge_base=knowledge_base)

        # 初始化真题数据库
        print("📚 正在加载真题数据库...")
        exam_db = ExamDatabase()
        exam_db.connect()

        print("✅ 服务初始化成功！")
        return True
    except Exception as e:
        print(f"❌ 服务初始化失败: {str(e)}")
        traceback.print_exc()
        return False


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '服务运行正常'
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取知识库统计信息"""
    try:
        if not knowledge_base:
            return jsonify({
                'success': False,
                'error': '知识库未初始化'
            }), 500
        
        stats = knowledge_base.get_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """问答接口"""
    try:
        # 检查服务是否已初始化
        if not ai_agent:
            return jsonify({
                'success': False,
                'error': 'AI Agent 未初始化'
            }), 500
        
        # 获取请求数据
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': '请提供问题内容'
            }), 400
        
        question = data['question']
        subject_filter = data.get('subject_filter', None)
        n_context = data.get('n_context', 5)
        
        # 调用 AI Agent 回答问题
        answer = ai_agent.answer(
            question=question,
            subject_filter=subject_filter,
            n_context=n_context
        )
        
        return jsonify({
            'success': True,
            'data': {
                'question': question,
                'answer': answer
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search', methods=['POST'])
def search_knowledge():
    """知识检索接口"""
    try:
        if not knowledge_base:
            return jsonify({
                'success': False,
                'error': '知识库未初始化'
            }), 500
        
        # 获取请求数据
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': '请提供查询内容'
            }), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        subject_filter = data.get('subject_filter', None)
        
        # 检索知识库
        results = knowledge_base.search(
            query=query,
            n_results=n_results,
            subject_filter=subject_filter
        )
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """获取科目列表"""
    subjects = [
        {'id': '工程经济', 'name': '工程经济'},
        {'id': '机电实务', 'name': '机电实务'},
        {'id': '法律法规', 'name': '法律法规'},
        {'id': '项目管理', 'name': '项目管理'}
    ]

    return jsonify({
        'success': True,
        'data': subjects
    })


@app.route('/api/exam/stats', methods=['GET'])
def get_exam_stats():
    """获取真题统计信息"""
    try:
        if not exam_db:
            return jsonify({
                'success': False,
                'error': '真题数据库未初始化'
            }), 500

        stats = exam_db.get_statistics()

        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/exam/questions', methods=['GET'])
def get_exam_questions():
    """获取真题列表（选择题）"""
    try:
        if not exam_db:
            return jsonify({
                'success': False,
                'error': '真题数据库未初始化'
            }), 500

        # 获取查询参数
        subject = request.args.get('subject')
        year = request.args.get('year', type=int)
        qtype = request.args.get('type')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)

        # 查询题目
        questions = exam_db.get_questions(
            subject=subject,
            year=year,
            qtype=qtype,
            page=page,
            page_size=page_size
        )

        return jsonify({
            'success': True,
            'data': questions
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/exam/cases', methods=['GET'])
def get_exam_cases():
    """获取案例题列表"""
    try:
        if not exam_db:
            return jsonify({
                'success': False,
                'error': '真题数据库未初始化'
            }), 500

        # 获取查询参数
        subject = request.args.get('subject')
        year = request.args.get('year', type=int)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)

        # 查询案例题
        cases = exam_db.get_case_studies(
            subject=subject,
            year=year,
            page=page,
            page_size=page_size
        )

        return jsonify({
            'success': True,
            'data': cases
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/exam/search', methods=['POST'])
def search_exam_questions():
    """搜索真题"""
    try:
        if not exam_db:
            return jsonify({
                'success': False,
                'error': '真题数据库未初始化'
            }), 500

        # 获取请求数据
        data = request.get_json()

        if not data or 'keyword' not in data:
            return jsonify({
                'success': False,
                'error': '请提供搜索关键词'
            }), 400

        keyword = data['keyword']
        subject = data.get('subject')
        year = data.get('year')
        limit = data.get('limit', 20)

        # 搜索题目
        results = exam_db.search_questions(
            keyword=keyword,
            subject=subject,
            year=year,
            limit=limit
        )

        return jsonify({
            'success': True,
            'data': {
                'keyword': keyword,
                'results': results
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/exam/ai-analysis', methods=['POST'])
def ai_analysis():
    """
    AI 解析题目
    请求体: {
        "question": "题目内容",
        "options": {"A": "选项A", "B": "选项B", ...},
        "answer": "正确答案",
        "subject": "科目"
    }
    """
    try:
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: question'
            }), 400

        question = data.get('question')
        options = data.get('options', {})
        answer = data.get('answer', '')
        subject = data.get('subject', '')

        # 构建提示词
        prompt = f"""请结合教材知识，详细解析以下题目：

题目：{question}

"""

        if options:
            prompt += "选项：\n"
            for key, value in options.items():
                prompt += f"{key}. {value}\n"
            prompt += "\n"

        if answer:
            prompt += f"正确答案：{answer}\n\n"

        prompt += """请从以下几个方面进行解析：
1. 知识点分析：这道题考查的核心知识点是什么？
2. 解题思路：如何分析和解答这道题？
3. 教材依据：相关知识点在教材中的位置和内容
4. 易错点提示：容易出错的地方和注意事项

请用清晰、易懂的语言进行解析。"""

        # 调用 AI（返回的是字符串，包含答案和引用）
        analysis_text = ai_agent.answer(prompt, subject_filter=subject if subject else None)

        # 从知识库检索相关内容作为来源
        contexts = knowledge_base.search(question, n_results=3, subject_filter=subject if subject else None)
        sources = []
        for ctx in contexts:
            sources.append({
                'subject': ctx.get('subject', ''),
                'content': ctx.get('content', '')[:200] + '...'  # 截取前200字符
            })

        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis_text,
                'sources': sources
            }
        })

    except Exception as e:
        print(f"❌ AI解析失败: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'AI解析失败: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'success': False,
        'error': '接口不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 一建机电备考 AI 助手 - API 服务器")
    print("=" * 60 + "\n")
    
    # 初始化服务
    if not init_services():
        print("\n❌ 服务初始化失败，请检查配置")
        return
    
    # 获取配置
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5001))
    debug = os.getenv('API_DEBUG', 'False').lower() == 'true'
    
    print(f"\n📡 API 服务器配置:")
    print(f"   地址: http://{host}:{port}")
    print(f"   调试模式: {debug}")
    print(f"\n📚 可用接口:")
    print(f"   GET  /api/health           - 健康检查")
    print(f"   GET  /api/stats            - 获取知识库统计信息")
    print(f"   GET  /api/subjects         - 获取科目列表")
    print(f"   POST /api/ask              - 问答接口")
    print(f"   POST /api/search           - 知识检索接口")
    print(f"\n📝 真题接口:")
    print(f"   GET  /api/exam/stats       - 获取真题统计信息")
    print(f"   GET  /api/exam/questions   - 获取真题列表（选择题）")
    print(f"   GET  /api/exam/cases       - 获取案例题列表")
    print(f"   POST /api/exam/search      - 搜索真题")
    print(f"   POST /api/exam/ai-analysis - AI解析题目")
    print(f"\n" + "=" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")
    
    # 启动服务器
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")


if __name__ == '__main__':
    main()

