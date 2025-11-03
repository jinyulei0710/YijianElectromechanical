#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一建历年真题查看器
功能：交互式查看和搜索真题
"""

import sys
from exam_database import ExamDatabase


class ExamViewer:
    """真题查看器"""
    
    def __init__(self):
        self.db = ExamDatabase()
        self.db.connect()
        
    def show_menu(self):
        """显示菜单"""
        print("\n" + "=" * 60)
        print("🎓 一建历年真题查看器")
        print("=" * 60)
        print("\n请选择功能:")
        print("  1. 查看统计信息")
        print("  2. 按科目浏览")
        print("  3. 按年份浏览")
        print("  4. 搜索题目")
        print("  5. 随机练习")
        print("  0. 退出")
        print("")
    
    def show_statistics(self):
        """显示统计信息"""
        print("\n" + "=" * 60)
        print("📊 真题库统计信息")
        print("=" * 60)
        
        stats = self.db.get_statistics()
        
        print(f"\n总题目数: {stats['total_questions']} 道")
        
        print("\n📚 按科目统计:")
        for subject, count in sorted(stats['by_subject'].items()):
            print(f"  {subject:12s}: {count:4d} 道")
        
        print("\n📅 按年份统计:")
        for year, count in sorted(stats['by_year'].items(), reverse=True):
            print(f"  {year} 年: {count:4d} 道")
        
        print("\n📝 按题型统计:")
        for qtype, count in sorted(stats['by_type'].items()):
            print(f"  {qtype:12s}: {count:4d} 道")
    
    def browse_by_subject(self):
        """按科目浏览"""
        print("\n请选择科目:")
        subjects = ['机电实务', '工程经济', '项目管理', '法律法规']
        for i, subject in enumerate(subjects, 1):
            print(f"  {i}. {subject}")
        
        choice = input("\n请输入序号: ").strip()
        
        try:
            subject = subjects[int(choice) - 1]
            self.show_questions(subject=subject)
        except (ValueError, IndexError):
            print("❌ 无效的选择")
    
    def browse_by_year(self):
        """按年份浏览"""
        year = input("\n请输入年份 (如 2023): ").strip()
        
        try:
            year = int(year)
            self.show_questions(year=year)
        except ValueError:
            print("❌ 无效的年份")
    
    def search_questions(self):
        """搜索题目"""
        keyword = input("\n请输入搜索关键词: ").strip()
        
        if keyword:
            self.show_questions(keyword=keyword)
        else:
            print("❌ 请输入关键词")
    
    def show_questions(self, keyword=None, subject=None, year=None, limit=10):
        """显示题目列表"""
        questions = self.db.search_questions(
            keyword=keyword,
            subject=subject,
            year=year,
            limit=limit
        )
        
        if not questions:
            print("\n❌ 未找到符合条件的题目")
            return
        
        print(f"\n找到 {len(questions)} 道题目:")
        print("=" * 60)
        
        for i, q in enumerate(questions, 1):
            print(f"\n【题目 {i}】")
            print(f"年份: {q['year']} | 科目: {q['subject']} | 题号: {q['number']} | 类型: {q['type']}")
            print(f"\n{q['question']}")
            
            if q['options']:
                print("\n选项:")
                for key in sorted(q['options'].keys()):
                    print(f"  {key}. {q['options'][key]}")
            
            if q['answer']:
                show_answer = input("\n是否显示答案? (y/n): ").strip().lower()
                if show_answer == 'y':
                    print(f"\n✅ 答案: {q['answer']}")
                    if q['analysis']:
                        print(f"\n📖 解析: {q['analysis']}")
            
            if i < len(questions):
                cont = input("\n按 Enter 继续，输入 q 返回: ").strip().lower()
                if cont == 'q':
                    break
    
    def random_practice(self):
        """随机练习"""
        print("\n🎲 随机练习模式")
        
        count = input("请输入练习题目数量 (默认10): ").strip()
        count = int(count) if count.isdigit() else 10
        
        cursor = self.db.conn.cursor()
        cursor.execute(f'SELECT * FROM questions ORDER BY RANDOM() LIMIT {count}')
        
        questions = []
        for row in cursor.fetchall():
            q = dict(row)
            cursor.execute('SELECT option_key, option_value FROM options WHERE question_id = ?', (q['id'],))
            q['options'] = {r['option_key']: r['option_value'] for r in cursor.fetchall()}
            questions.append(q)
        
        if not questions:
            print("❌ 题库为空")
            return
        
        correct = 0
        total = len(questions)
        
        for i, q in enumerate(questions, 1):
            print(f"\n{'=' * 60}")
            print(f"第 {i}/{total} 题")
            print(f"{'=' * 60}")
            print(f"\n[{q['year']}年 {q['subject']}] ({q['type']})")
            print(f"\n{q['question']}")
            
            if q['options']:
                print("\n选项:")
                for key in sorted(q['options'].keys()):
                    print(f"  {key}. {q['options'][key]}")
            
            user_answer = input("\n你的答案: ").strip().upper()
            
            if q['answer']:
                if user_answer == q['answer']:
                    print("✅ 回答正确！")
                    correct += 1
                else:
                    print(f"❌ 回答错误！正确答案: {q['answer']}")
                
                if q['analysis']:
                    print(f"\n📖 解析: {q['analysis']}")
            else:
                print("⚠️  该题暂无答案")
            
            if i < total:
                input("\n按 Enter 继续...")
        
        print(f"\n{'=' * 60}")
        print(f"练习完成！正确率: {correct}/{total} ({correct*100//total}%)")
        print(f"{'=' * 60}")
    
    def run(self):
        """运行查看器"""
        while True:
            self.show_menu()
            choice = input("请选择 (0-5): ").strip()
            
            if choice == '0':
                print("\n👋 再见！")
                break
            elif choice == '1':
                self.show_statistics()
            elif choice == '2':
                self.browse_by_subject()
            elif choice == '3':
                self.browse_by_year()
            elif choice == '4':
                self.search_questions()
            elif choice == '5':
                self.random_practice()
            else:
                print("❌ 无效的选择，请重新输入")
        
        self.db.close()


def main():
    """主函数"""
    viewer = ExamViewer()
    viewer.run()


if __name__ == "__main__":
    main()

