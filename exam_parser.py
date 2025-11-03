#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一建历年真题解析程序
功能：解析PDF文件，提取题目、选项、答案和解析
"""

import re
import json
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ExamQuestion:
    """真题题目类"""
    
    def __init__(self):
        self.number = None  # 题号
        self.type = None  # 题型：单选、多选、案例
        self.question = None  # 题干
        self.options = {}  # 选项 {A: xxx, B: xxx, ...}
        self.answer = None  # 答案
        self.analysis = None  # 解析
        self.knowledge_points = []  # 知识点
        self.difficulty = None  # 难度
        
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'number': self.number,
            'type': self.type,
            'question': self.question,
            'options': self.options,
            'answer': self.answer,
            'analysis': self.analysis,
            'knowledge_points': self.knowledge_points,
            'difficulty': self.difficulty
        }


class ExamPDFParser:
    """真题PDF解析器"""
    
    def __init__(self):
        self.questions = []
        
    def parse_pdf(self, pdf_path: str) -> List[ExamQuestion]:
        """解析PDF文件"""
        print(f"\n📄 正在解析: {Path(pdf_path).name}")

        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""

                # 提取所有页面的文本
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"

                    if page_num % 10 == 0:
                        print(f"  已处理 {page_num}/{len(pdf.pages)} 页...")

                print(f"  ✅ 文本提取完成，共 {len(pdf.pages)} 页")

                # 特殊处理：2010年机电实务（答案在图片表格中）
                if '2010年' in Path(pdf_path).name and '机电' in Path(pdf_path).name:
                    print(f"  🖼️  检测到2010年机电实务，使用图片表格答案...")
                    questions = self._parse_2010_jidian_with_image_answers(full_text, pdf)
                # 检测答案是否集中在后面
                elif '答案解析集中在最后' in Path(pdf_path).name or '解析在最后' in Path(pdf_path).name:
                    print(f"  🔍 检测到答案集中在后面，使用两阶段解析...")
                    questions = self._parse_questions_with_separate_answers(full_text)
                else:
                    # 解析题目
                    questions = self._parse_questions(full_text)

                print(f"  ✅ 解析完成，共提取 {len(questions)} 道题目")

                # 统计答案率
                with_answer = sum(1 for q in questions if q.answer)
                answer_rate = (with_answer * 100 // len(questions)) if questions else 0
                print(f"  📊 答案率: {with_answer}/{len(questions)} ({answer_rate}%)")

                return questions

        except Exception as e:
            print(f"  ❌ 解析失败: {str(e)}")
            return []

    def _parse_2010_jidian_with_image_answers(self, text: str, pdf) -> List[ExamQuestion]:
        """
        特殊处理2010年机电实务PDF（答案在图片表格中）
        使用OCR或手动硬编码的答案
        """
        # 第一阶段：解析题目
        questions = self._parse_questions(text)

        # 第二阶段：硬编码答案（从图片表格中手动提取）
        # 单选题答案（1-20题）- 需要手动从图片中提取
        single_choice_answers = {
            # TODO: 从图片中手动提取单选题答案
            # 暂时使用OCR识别到的部分答案
        }

        # 多选题答案（21-30题）- 从OCR成功识别
        multi_choice_answers = {
            21: 'BDE',
            22: 'BCD',
            23: 'BCE',
            24: 'ACD',
            25: 'BCE',
            26: 'ABC',
            27: 'BCDE',
            28: 'ACD',
            29: 'BCD',
            30: 'BDE'
        }

        # 合并答案
        all_answers = {**single_choice_answers, **multi_choice_answers}

        # 第三阶段：将答案匹配到题目
        matched = 0
        for question in questions:
            if question.number in all_answers:
                question.answer = all_answers[question.number]
                matched += 1

        print(f"  🔗 答案匹配: {matched}/{len(questions)} 道题目")
        print(f"  ⚠️  单选题答案需要手动补充（当前仅有多选题答案）")
        return questions

    def _parse_questions_with_separate_answers(self, text: str) -> List[ExamQuestion]:
        """两阶段解析：题目和答案分离的情况"""
        # 第一阶段：解析题目
        questions = self._parse_questions(text)

        # 第二阶段：提取答案区域并匹配
        answers_dict = self._extract_answers_section(text)

        # 第三阶段：将答案匹配到题目
        matched = 0
        for question in questions:
            if question.number in answers_dict:
                answer_info = answers_dict[question.number]
                question.answer = answer_info.get('answer')
                question.analysis = answer_info.get('analysis')
                matched += 1

        print(f"  🔗 答案匹配: {matched}/{len(questions)} 道题目")
        return questions

    def _extract_answers_section(self, text: str) -> dict:
        """提取答案区域"""
        answers = {}

        # 查找答案区域的开始标记
        answer_markers = [
            r'参考答案及解析',
            r'参考答案',
            r'答案及解析',
            r'答案解析',
            r'一、单项选择题.*?答案',
        ]

        # 尝试找到答案区域
        answer_section = ""
        for marker in answer_markers:
            match = re.search(marker, text, re.IGNORECASE)
            if match:
                # 从标记位置开始提取后续内容
                answer_section = text[match.start():]
                print(f"  📍 找到答案区域标记: {marker}")
                break

        if not answer_section:
            # 如果没找到明确标记，尝试从后半部分查找
            # 通常答案在文档的后40%部分
            split_point = len(text) * 3 // 5
            answer_section = text[split_point:]
            print(f"  📍 使用后半部分作为答案区域")

        # 特殊处理：机电实务的空格分隔格式
        # 格式: 一、单项选择题(共20题) 1 D 2 B 3 A ...
        #      二、多项选择题(共10题) 1 ABCE 2 ACE ...
        if self._try_extract_spaced_answers(answer_section, answers):
            return answers

        # 解析答案
        # 格式1: 1.【答案】A
        # 格式2: 1. 答案：A
        # 格式3: 【1】答案：A
        # 格式4: 1.A (简单格式)
        # 格式5: 1参考答案： A,B,C
        # 格式6: 1 D 2 B 3 A (空格分隔，机电实务常见)
        patterns = [
            (r'(\d+)[.、．]\s*【答案】\s*([A-E,，]+)', '【答案】格式'),
            (r'(\d+)[.、．]\s*答案[：:]\s*([A-E,，]+)', '答案：格式'),
            (r'(\d+)\s*参考答案[：:]\s*([A-E,，\s]+)', '参考答案：格式'),
            (r'【(\d+)】\s*答案[：:]\s*([A-E,，]+)', '【题号】答案：格式'),
            (r'(\d+)[.、．]\s*\[答案\]\s*([A-E,，]+)', '[答案]格式'),
            (r'(?:^|\n)(\d+)\s+([A-E]+)(?=\s+\d+\s+[A-E]+|\s*\n)', '空格分隔格式'),  # 新增
            (r'(\d+)[.、．]\s*([A-E]+)\s*(?:\n|【解析】)', '简单格式'),
        ]

        total_found = 0
        for pattern, desc in patterns:
            matches = list(re.finditer(pattern, answer_section, re.MULTILINE))
            if matches:
                print(f"  🔍 使用 {desc} 找到 {len(matches)} 个答案")
                for match in matches:
                    num = int(match.group(1))
                    answer = match.group(2).strip()

                    # 清理答案：移除逗号、空格、中文逗号
                    answer = answer.replace(',', '').replace('，', '').replace(' ', '').replace('\n', '')
                    # 只保留A-E字母
                    answer = ''.join(c for c in answer if c in 'ABCDE')

                    if num not in answers and answer:
                        answers[num] = {}
                        total_found += 1
                    if answer:
                        answers[num]['answer'] = answer

        print(f"  ✅ 共提取 {total_found} 个答案")

        # 提取解析
        analysis_patterns = [
            r'(\d+)[.、．]\s*【解析】(.*?)(?=\d+[.、．]|$)',
            r'【解析】(.*?)(?=\d+[.、．]|【答案】|$)',
        ]

        for pattern in analysis_patterns:
            matches = re.finditer(pattern, answer_section, re.MULTILINE | re.DOTALL)
            for match in matches:
                if len(match.groups()) == 2:
                    num = int(match.group(1))
                    analysis = match.group(2).strip()

                    if num in answers:
                        # 清理解析文本
                        analysis = re.sub(r'\s+', ' ', analysis)  # 合并空白
                        answers[num]['analysis'] = analysis[:500]  # 限制长度

        return answers

    def _try_extract_spaced_answers(self, answer_section: str, answers: dict) -> bool:
        """
        尝试提取空格分隔格式的答案
        格式: 一、单项选择题(共20题，每题1分)
             1 D 2 B 3 A 4 D 5 C
             6 A 7 A 8 C 9 C 10 B
             二、多项选择题(共10题，每题2分)
             1 ABCE 2 ACE 3 ABCD
        """
        # 查找单选题答案区域
        single_match = re.search(
            r'一、\s*单项选择题.*?\n(.*?)(?=二、|三、|$)',
            answer_section,
            re.DOTALL
        )

        # 查找多选题答案区域
        multi_match = re.search(
            r'二、\s*多项选择题.*?\n(.*?)(?=三、|$)',
            answer_section,
            re.DOTALL
        )

        total_found = 0

        # 提取单选题答案
        if single_match:
            single_text = single_match.group(1)
            # 提取所有 "数字 字母" 对
            pattern = r'(\d+)\s+([A-E])\b'
            matches = re.findall(pattern, single_text)

            if matches:
                print(f"  🔍 使用 空格分隔格式(单选) 找到 {len(matches)} 个答案")
                for num_str, answer in matches:
                    num = int(num_str)
                    if num not in answers:
                        answers[num] = {}
                        total_found += 1
                    answers[num]['answer'] = answer

        # 提取多选题答案
        if multi_match:
            multi_text = multi_match.group(1)
            # 提取所有 "数字 多个字母" 对
            pattern = r'(\d+)\s+([A-E]{2,})\b'
            matches = re.findall(pattern, multi_text)

            if matches:
                print(f"  🔍 使用 空格分隔格式(多选) 找到 {len(matches)} 个答案")
                # 多选题题号需要加上单选题的数量
                # 通常单选题20道，多选题从21开始
                # 但答案中多选题题号又从1开始，需要推算

                # 先找出单选题的最大题号
                max_single = 0
                for num in answers.keys():
                    if answers[num].get('answer') and len(answers[num]['answer']) == 1:
                        max_single = max(max_single, num)

                for num_str, answer in matches:
                    num = int(num_str)
                    # 多选题的实际题号 = 单选题数量 + 多选题序号
                    actual_num = max_single + num
                    if actual_num not in answers:
                        answers[actual_num] = {}
                        total_found += 1
                    answers[actual_num]['answer'] = answer

        if total_found > 0:
            print(f"  ✅ 共提取 {total_found} 个答案")
            return True

        return False

    def _parse_questions(self, text: str) -> List[ExamQuestion]:
        """从文本中解析题目"""
        questions = []

        # 检测题型范围（通过章节标题）
        type_ranges = self._detect_question_type_ranges(text)

        # 分离案例题部分（题目部分）
        case_section_match = re.search(r'三、\s*案例.*?题.*?(?=参考答案|$)', text, re.DOTALL | re.IGNORECASE)
        case_section = ""
        main_text = text

        if case_section_match:
            case_section = case_section_match.group(0)
            # 从主文本中移除案例题部分，避免重复解析
            main_text = text[:case_section_match.start()]

            # 同时移除答案部分的案例题答案（避免案例题小问题被当成单选题）
            # 查找答案区域中的案例题部分
            answer_start = re.search(r'参考答案', text, re.IGNORECASE)
            if answer_start:
                answer_text = text[answer_start.start():]
                # 在答案区域中查找案例题答案的开始
                case_answer_match = re.search(r'[（(][一二三四五][）)]', answer_text)
                if case_answer_match:
                    # 保留答案区域中案例题之前的部分（单选题和多选题答案）
                    main_text += answer_text[:case_answer_match.start()]
                else:
                    main_text += answer_text

            print(f"  📋 检测到案例题部分，已移除（案例题使用独立解析器 case_parser.py）")

        # 解析选择题（单选+多选）
        # 先尝试标准格式（有标点）
        question_pattern = r'(?:^|\n)(\d+)[.、．]\s*'
        parts = re.split(question_pattern, main_text)

        # 如果没有找到题目，尝试无标点格式
        if len(parts) < 10:  # 题目太少，可能是格式不对
            print(f"  🔄 标准格式未找到足够题目，尝试无标点格式...")
            # 匹配：数字后直接跟汉字（如"1根据"）
            question_pattern = r'(?:^|\n)(\d+)(?=[一-龥])'
            parts = re.split(question_pattern, main_text)

        # 跳过第一个空白部分
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                question_num = parts[i]
                question_text = parts[i + 1]

                question = self._parse_single_question(question_num, question_text, type_ranges)
                if question:
                    questions.append(question)

        # 注意：案例题不在这里解析
        # 案例题使用独立的解析器 case_parser.py
        # 案例题数据保存在 机电实务_案例题.json 文件中

        return questions

    # 注意：案例题解析已移至独立的 case_parser.py
    # 此方法已废弃，保留仅为兼容性

    def _detect_question_type_ranges(self, text: str) -> dict:
        """检测题型范围（通过章节标题）"""
        type_ranges = {}

        # 查找单选题标记
        single_match = re.search(r'一、\s*单.*?选.*?题.*?共\s*(\d+)\s*题', text, re.IGNORECASE)
        if single_match:
            single_count = int(single_match.group(1))
            type_ranges['单选题'] = (1, single_count)
            print(f"  📌 检测到单选题范围: 1-{single_count}")

        # 查找多选题标记
        multi_match = re.search(r'二、\s*多.*?选.*?题.*?共\s*(\d+)\s*题', text, re.IGNORECASE)
        if multi_match:
            multi_count = int(multi_match.group(1))
            single_end = type_ranges.get('单选题', (0, 0))[1]
            type_ranges['多选题'] = (single_end + 1, single_end + multi_count)
            print(f"  📌 检测到多选题范围: {single_end + 1}-{single_end + multi_count}")

        # 查找案例题标记
        case_match = re.search(r'三、\s*案例.*?题.*?共\s*(\d+)\s*题', text, re.IGNORECASE)
        if case_match:
            case_count = int(case_match.group(1))
            multi_end = type_ranges.get('多选题', (0, 0))[1]
            if multi_end == 0:
                single_end = type_ranges.get('单选题', (0, 0))[1]
                multi_end = single_end
            type_ranges['案例题'] = (multi_end + 1, multi_end + case_count)
            print(f"  📌 检测到案例题范围: {multi_end + 1}-{multi_end + case_count}")

        return type_ranges
    
    def _parse_single_question(self, num: str, text: str, type_ranges: dict = None) -> Optional[ExamQuestion]:
        """解析单个题目"""
        question = ExamQuestion()
        question.number = int(num)

        # 判断题型（优先使用题型范围）
        if type_ranges:
            for qtype, (start, end) in type_ranges.items():
                if start <= question.number <= end:
                    question.type = qtype
                    break

        # 如果没有通过范围判断出题型，使用文本特征判断
        if not question.type:
            if '（多选题）' in text or '【多选题】' in text or self._is_multi_choice(text):
                question.type = '多选题'
            elif '（案例题）' in text or '【案例题】' in text or '背景资料' in text:
                question.type = '案例题'
            else:
                question.type = '单选题'

        # 提取题干和选项
        self._extract_question_and_options(question, text)

        # 提取答案
        self._extract_answer(question, text)

        # 提取解析
        self._extract_analysis(question, text)

        return question if question.question else None
    
    def _is_multi_choice(self, text: str) -> bool:
        """判断是否为多选题"""
        # 如果答案包含多个字母，可能是多选题
        answer_match = re.search(r'答案[：:]\s*([A-E]+)', text)
        if answer_match:
            answer = answer_match.group(1)
            return len(answer) > 1
        return False
    
    def _extract_question_and_options(self, question: ExamQuestion, text: str):
        """提取题干和选项"""
        # 移除题型标记
        text = re.sub(r'[（【](?:单选题|多选题|案例题)[）】]', '', text)
        
        # 查找选项开始位置
        option_pattern = r'\n\s*([A-E])[.、．]'
        option_matches = list(re.finditer(option_pattern, text))
        
        if option_matches:
            # 题干是选项之前的内容
            question.question = text[:option_matches[0].start()].strip()
            
            # 提取选项
            for i, match in enumerate(option_matches):
                option_letter = match.group(1)
                start = match.end()
                end = option_matches[i + 1].start() if i + 1 < len(option_matches) else len(text)
                
                option_text = text[start:end].strip()
                # 移除答案和解析部分
                option_text = re.split(r'答案[：:]|解析[：:]|【答案】|【解析】', option_text)[0].strip()
                
                question.options[option_letter] = option_text
        else:
            # 没有选项的情况（可能是案例题）
            question.question = text.strip()
    
    def _extract_answer(self, question: ExamQuestion, text: str):
        """提取答案"""
        # 匹配答案模式
        patterns = [
            r'答案[：:]\s*([A-E]+)',
            r'【答案】\s*([A-E]+)',
            r'正确答案[：:]\s*([A-E]+)',
            r'\n\s*([A-E]+)\s*(?:正确|√)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                question.answer = match.group(1)
                break
    
    def _extract_analysis(self, question: ExamQuestion, text: str):
        """提取解析"""
        # 匹配解析模式
        patterns = [
            r'解析[：:](.*?)(?=\n\d+[.、．]|$)',
            r'【解析】(.*?)(?=\n\d+[.、．]|$)',
            r'答案解析[：:](.*?)(?=\n\d+[.、．]|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                question.analysis = match.group(1).strip()
                break
    
    def save_to_json(self, questions: List[ExamQuestion], output_file: str):
        """保存为JSON文件"""
        data = {
            'total': len(questions),
            'questions': [q.to_dict() for q in questions]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存到: {output_file}")


class ExamBatchParser:
    """批量解析器"""
    
    def __init__(self, index_file: str = "./机电历年真题/exam_files_index.json"):
        self.index_file = index_file
        self.parser = ExamPDFParser()
        
    def load_index(self) -> Dict:
        """加载文件索引"""
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_by_subject(self, subject: str, max_files: int = 3):
        """按科目解析（限制数量用于测试）"""
        print("\n" + "=" * 60)
        print(f"📚 开始解析科目: {subject}")
        print("=" * 60)
        
        index_data = self.load_index()
        subject_files = index_data['subjects'].get(subject, [])
        
        if not subject_files:
            print(f"❌ 未找到科目 {subject} 的文件")
            return
        
        # 选择包含"答案+解析"的文件
        target_files = [
            f for f in subject_files 
            if '真题+答案+解析' in f['file_type']
        ][:max_files]
        
        print(f"找到 {len(target_files)} 个文件（限制 {max_files} 个）")
        
        all_questions = []
        
        for file_info in target_files:
            pdf_path = file_info['path']
            year = file_info['year']
            
            questions = self.parser.parse_pdf(pdf_path)
            
            # 添加年份和科目信息
            for q in questions:
                q_dict = q.to_dict()
                q_dict['year'] = year
                q_dict['subject'] = subject
                all_questions.append(q_dict)
        
        # 保存结果
        output_dir = Path("./机电历年真题/parsed_data")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{subject}_questions.json"
        
        data = {
            'subject': subject,
            'total_questions': len(all_questions),
            'files_parsed': len(target_files),
            'questions': all_questions
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ {subject} 解析完成！")
        print(f"   文件数: {len(target_files)}")
        print(f"   题目数: {len(all_questions)}")
        print(f"   保存至: {output_file}")
        
        return all_questions


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🎓 一建历年真题解析程序")
    print("=" * 60)
    
    batch_parser = ExamBatchParser()
    
    # 测试解析（每个科目解析3个文件）
    subjects = ['机电实务', '工程经济', '项目管理', '法律法规']
    
    print("\n💡 提示: 为了快速测试，每个科目只解析前3个文件")
    print("    如需解析全部文件，请修改 max_files 参数\n")
    
    for subject in subjects:
        try:
            batch_parser.parse_by_subject(subject, max_files=3)
        except Exception as e:
            print(f"❌ {subject} 解析失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ 批量解析完成！")
    print("=" * 60)
    print("\n💡 下一步:")
    print("  1. 查看 机电历年真题/parsed_data/ 目录下的JSON文件")
    print("  2. 运行 exam_database.py 构建真题数据库")
    print("  3. 集成到AI助手系统")
    print("")


if __name__ == "__main__":
    main()

