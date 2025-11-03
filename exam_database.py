#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一建历年真题数据库构建程序
功能：将解析的真题数据构建为可查询的数据库
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class ExamDatabase:
    """真题数据库"""

    def __init__(self, db_path: str = "./data/exam_questions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None

    def connect(self):
        """连接数据库"""
        # 使用 check_same_thread=False 允许多线程访问
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def _get_connection(self):
        """获取数据库连接（线程安全）"""
        if self.conn is None:
            self.connect()
        return self.conn
    
    def create_tables(self):
        """创建数据表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建题目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                subject TEXT NOT NULL,
                number INTEGER NOT NULL,
                type TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT,
                analysis TEXT,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(year, subject, number)
            )
        ''')

        # 创建选项表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                option_key TEXT NOT NULL,
                option_value TEXT NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questions(id),
                UNIQUE(question_id, option_key)
            )
        ''')

        # 创建知识点表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                point TEXT NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
        ''')

        # 创建案例题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_studies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                subject TEXT NOT NULL,
                case_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                background TEXT NOT NULL,
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(year, subject, case_number)
            )
        ''')

        # 创建案例题小问题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_sub_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                sub_number INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT,
                analysis TEXT,
                FOREIGN KEY (case_id) REFERENCES case_studies(id),
                UNIQUE(case_id, sub_number)
            )
        ''')

        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON questions(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_subject ON questions(subject)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON questions(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_case_year ON case_studies(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_case_subject ON case_studies(subject)')

        conn.commit()
        print("✅ 数据表创建成功")
    
    def import_from_json(self, json_file: str):
        """从JSON文件导入数据"""
        print(f"\n📥 导入数据: {Path(json_file).name}")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn = self._get_connection()
        cursor = conn.cursor()
        imported = 0
        skipped = 0
        
        for q in data['questions']:
            try:
                # 插入题目
                cursor.execute('''
                    INSERT OR IGNORE INTO questions 
                    (year, subject, number, type, question, answer, analysis, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    q['year'],
                    q['subject'],
                    q['number'],
                    q['type'],
                    q['question'],
                    q.get('answer'),
                    q.get('analysis'),
                    q.get('difficulty')
                ))
                
                if cursor.rowcount > 0:
                    question_id = cursor.lastrowid
                    
                    # 插入选项
                    for key, value in q.get('options', {}).items():
                        cursor.execute('''
                            INSERT OR IGNORE INTO options (question_id, option_key, option_value)
                            VALUES (?, ?, ?)
                        ''', (question_id, key, value))
                    
                    # 插入知识点
                    for point in q.get('knowledge_points', []):
                        cursor.execute('''
                            INSERT INTO knowledge_points (question_id, point)
                            VALUES (?, ?)
                        ''', (question_id, point))
                    
                    imported += 1
                else:
                    skipped += 1
                    
            except Exception as e:
                print(f"  ⚠️  导入题目 {q.get('number')} 失败: {str(e)}")
                skipped += 1

        conn.commit()
        print(f"  ✅ 导入 {imported} 道题目，跳过 {skipped} 道")

        return imported, skipped

    def import_case_studies_from_json(self, json_file: str):
        """从JSON文件导入案例题数据"""
        print(f"\n📥 导入案例题数据: {Path(json_file).name}")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn = self._get_connection()
        cursor = conn.cursor()
        imported_cases = 0
        imported_subs = 0
        skipped = 0

        for case in data['case_studies']:
            try:
                # 插入案例题
                cursor.execute('''
                    INSERT OR IGNORE INTO case_studies
                    (year, subject, case_number, title, background, score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    case['year'],
                    case['subject'],
                    case['case_number'],
                    case['title'],
                    case['background'],
                    case.get('score')
                ))

                if cursor.rowcount > 0:
                    case_id = cursor.lastrowid

                    # 插入小问题
                    for sq in case['sub_questions']:
                        cursor.execute('''
                            INSERT OR IGNORE INTO case_sub_questions
                            (case_id, sub_number, question, answer, analysis)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            case_id,
                            sq['sub_number'],
                            sq['question'],
                            sq.get('answer'),
                            sq.get('analysis')
                        ))
                        if cursor.rowcount > 0:
                            imported_subs += 1

                    imported_cases += 1
                else:
                    skipped += 1

            except Exception as e:
                print(f"  ⚠️  导入案例 {case.get('case_number')} 失败: {str(e)}")
                skipped += 1

        conn.commit()
        print(f"  ✅ 导入 {imported_cases} 个案例，{imported_subs} 个小问题，跳过 {skipped} 个")

        return imported_cases, imported_subs, skipped

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        # 总题目数（选择题）
        cursor.execute('SELECT COUNT(*) FROM questions')
        stats['total_questions'] = cursor.fetchone()[0]

        # 总案例数
        cursor.execute('SELECT COUNT(*) FROM case_studies')
        stats['total_cases'] = cursor.fetchone()[0]

        # 总案例小问题数
        cursor.execute('SELECT COUNT(*) FROM case_sub_questions')
        stats['total_case_sub_questions'] = cursor.fetchone()[0]

        # 按科目统计（选择题）
        cursor.execute('''
            SELECT subject, COUNT(*) as count
            FROM questions
            GROUP BY subject
        ''')
        stats['by_subject'] = {row['subject']: row['count'] for row in cursor.fetchall()}

        # 按科目统计（案例题）
        cursor.execute('''
            SELECT subject, COUNT(*) as count
            FROM case_studies
            GROUP BY subject
        ''')
        stats['cases_by_subject'] = {row['subject']: row['count'] for row in cursor.fetchall()}

        # 按年份统计（选择题）
        cursor.execute('''
            SELECT year, COUNT(*) as count
            FROM questions
            GROUP BY year
            ORDER BY year DESC
        ''')
        stats['by_year'] = {row['year']: row['count'] for row in cursor.fetchall()}

        # 按年份统计（案例题）
        cursor.execute('''
            SELECT year, COUNT(*) as count
            FROM case_studies
            GROUP BY year
            ORDER BY year DESC
        ''')
        stats['cases_by_year'] = {row['year']: row['count'] for row in cursor.fetchall()}

        # 按题型统计
        cursor.execute('''
            SELECT type, COUNT(*) as count
            FROM questions
            GROUP BY type
        ''')
        stats['by_type'] = {row['type']: row['count'] for row in cursor.fetchall()}

        return stats
    
    def search_questions(self, keyword: str = None, subject: str = None,
                        year: int = None, limit: int = 10) -> List[Dict]:
        """搜索题目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM questions WHERE 1=1'
        params = []
        
        if keyword:
            query += ' AND question LIKE ?'
            params.append(f'%{keyword}%')
        
        if subject:
            query += ' AND subject = ?'
            params.append(subject)
        
        if year:
            query += ' AND year = ?'
            params.append(year)
        
        query += f' LIMIT {limit}'
        
        cursor.execute(query, params)
        
        questions = []
        for row in cursor.fetchall():
            q = dict(row)
            
            # 获取选项
            cursor.execute('SELECT option_key, option_value FROM options WHERE question_id = ?', (q['id'],))
            q['options'] = {r['option_key']: r['option_value'] for r in cursor.fetchall()}
            
            questions.append(q)
        
        return questions

    def get_questions(self, subject: str = None, year: int = None,
                     qtype: str = None, page: int = 1, page_size: int = 20) -> Dict:
        """分页获取题目"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 构建查询条件
        query = 'SELECT * FROM questions WHERE 1=1'
        count_query = 'SELECT COUNT(*) FROM questions WHERE 1=1'
        params = []

        if subject:
            query += ' AND subject = ?'
            count_query += ' AND subject = ?'
            params.append(subject)

        if year:
            query += ' AND year = ?'
            count_query += ' AND year = ?'
            params.append(year)

        if qtype:
            query += ' AND type = ?'
            count_query += ' AND type = ?'
            params.append(qtype)

        # 获取总数
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # 分页查询
        offset = (page - 1) * page_size
        query += f' ORDER BY year DESC, number ASC LIMIT {page_size} OFFSET {offset}'

        cursor.execute(query, params)

        questions = []
        for row in cursor.fetchall():
            q = dict(row)

            # 获取选项
            cursor.execute('SELECT option_key, option_value FROM options WHERE question_id = ?', (q['id'],))
            q['options'] = {r['option_key']: r['option_value'] for r in cursor.fetchall()}

            questions.append(q)

        return {
            'questions': questions,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def get_case_studies(self, subject: str = None, year: int = None,
                        page: int = 1, page_size: int = 10) -> Dict:
        """分页获取案例题"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 构建查询条件
        query = 'SELECT * FROM case_studies WHERE 1=1'
        count_query = 'SELECT COUNT(*) FROM case_studies WHERE 1=1'
        params = []

        if subject:
            query += ' AND subject = ?'
            count_query += ' AND subject = ?'
            params.append(subject)

        if year:
            query += ' AND year = ?'
            count_query += ' AND year = ?'
            params.append(year)

        # 获取总数
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # 分页查询
        offset = (page - 1) * page_size
        query += f' ORDER BY year DESC, case_number ASC LIMIT {page_size} OFFSET {offset}'

        cursor.execute(query, params)

        cases = []
        for row in cursor.fetchall():
            case = dict(row)

            # 获取小问题
            cursor.execute('''
                SELECT sub_number, question, answer, analysis
                FROM case_sub_questions
                WHERE case_id = ?
                ORDER BY sub_number
            ''', (case['id'],))

            case['sub_questions'] = [dict(r) for r in cursor.fetchall()]

            cases.append(case)

        return {
            'cases': cases,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🗄️  一建历年真题数据库构建程序")
    print("=" * 60)
    
    # 创建数据库
    db = ExamDatabase()
    db.connect()
    db.create_tables()
    
    # 导入数据
    parsed_dir = Path("./机电历年真题/parsed_data")

    if not parsed_dir.exists():
        print("\n❌ 未找到解析数据目录，请先运行 exam_parser.py")
        return

    print("\n📂 扫描解析数据...")

    # 导入选择题
    json_files = list(parsed_dir.glob("*_questions.json"))
    print(f"找到 {len(json_files)} 个选择题数据文件")

    total_imported = 0
    total_skipped = 0

    for json_file in json_files:
        imported, skipped = db.import_from_json(json_file)
        total_imported += imported
        total_skipped += skipped

    # 导入案例题
    case_files = list(parsed_dir.glob("*_案例题.json"))
    print(f"\n找到 {len(case_files)} 个案例题数据文件")

    total_cases = 0
    total_case_subs = 0
    total_case_skipped = 0

    for case_file in case_files:
        cases, subs, skipped = db.import_case_studies_from_json(case_file)
        total_cases += cases
        total_case_subs += subs
        total_case_skipped += skipped
    
    # 显示统计信息
    print("\n" + "=" * 60)
    print("📊 数据库统计信息")
    print("=" * 60)

    stats = db.get_statistics()

    print(f"\n📝 选择题总数: {stats['total_questions']} 道")
    print(f"📋 案例题总数: {stats['total_cases']} 个（{stats['total_case_sub_questions']} 个小问题）")
    print(f"📊 总计: {stats['total_questions'] + stats['total_case_sub_questions']} 道题目")

    print("\n📚 选择题按科目统计:")
    for subject, count in sorted(stats['by_subject'].items()):
        print(f"  {subject:12s}: {count:4d} 道")

    print("\n📋 案例题按科目统计:")
    for subject, count in sorted(stats.get('cases_by_subject', {}).items()):
        print(f"  {subject:12s}: {count:4d} 个")

    print("\n📅 选择题按年份统计:")
    for year, count in sorted(stats['by_year'].items(), reverse=True):
        print(f"  {year} 年: {count:4d} 道")

    print("\n📅 案例题按年份统计:")
    for year, count in sorted(stats.get('cases_by_year', {}).items(), reverse=True):
        print(f"  {year} 年: {count:4d} 个")

    print("\n📝 按题型统计:")
    for qtype, count in sorted(stats['by_type'].items()):
        print(f"  {qtype:12s}: {count:4d} 道")
    
    # 测试搜索
    print("\n" + "=" * 60)
    print("🔍 搜索测试")
    print("=" * 60)
    
    print("\n搜索关键词: '施工'")
    results = db.search_questions(keyword='施工', limit=3)
    for i, q in enumerate(results, 1):
        print(f"\n{i}. [{q['year']}年 {q['subject']}] 第{q['number']}题 ({q['type']})")
        print(f"   {q['question'][:50]}...")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("✅ 数据库构建完成！")
    print("=" * 60)
    print(f"\n数据库文件: {db.db_path}")
    print(f"总导入: {total_imported} 道题目")
    print(f"总跳过: {total_skipped} 道题目")
    print("\n💡 下一步:")
    print("  1. 运行 exam_viewer.py 查看和搜索题目")
    print("  2. 集成到AI助手系统")
    print("")


if __name__ == "__main__":
    main()

