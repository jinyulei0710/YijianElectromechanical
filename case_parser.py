#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例题解析器 - 专门用于解析和管理案例题
"""

import re
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import pdfplumber


@dataclass
class SubQuestion:
    """案例题的小问题"""
    sub_number: int  # 小问题编号（1, 2, 3...）
    question: str  # 问题内容
    answer: Optional[str] = None  # 答案
    analysis: Optional[str] = None  # 解析


@dataclass
class CaseStudy:
    """案例题（案例分析题）"""
    case_number: int  # 案例编号（1, 2, 3, 4, 5）
    year: int  # 年份
    subject: str  # 科目
    title: str  # 案例标题（如"案例（一）"）
    background: str  # 背景资料
    sub_questions: List[SubQuestion]  # 小问题列表
    score: Optional[int] = None  # 分值
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'case_number': self.case_number,
            'year': self.year,
            'subject': self.subject,
            'title': self.title,
            'background': self.background,
            'score': self.score,
            'sub_questions': [asdict(sq) for sq in self.sub_questions]
        }


class CaseStudyParser:
    """案例题解析器"""
    
    def __init__(self):
        self.chinese_to_arabic = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
        }
    
    def parse_pdf(self, pdf_path: str, year: int, subject: str) -> List[CaseStudy]:
        """解析PDF中的案例题"""
        print(f"\n📄 解析案例题: {pdf_path}")
        
        # 提取文本
        text = self._extract_text(pdf_path)
        
        # 解析案例题
        case_studies = self._parse_case_studies(text, year, subject)
        
        print(f"  ✅ 共解析 {len(case_studies)} 个案例题")
        for cs in case_studies:
            print(f"    案例{cs.case_number}: {len(cs.sub_questions)}个小问题")
        
        return case_studies
    
    def _extract_text(self, pdf_path: str) -> str:
        """提取PDF文本"""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _parse_case_studies(self, text: str, year: int, subject: str) -> List[CaseStudy]:
        """解析案例题"""
        case_studies = []

        # 查找案例题部分 - 支持多种标题格式
        # 格式1：三、案例分析题
        # 格式2：三、实务操作和案例分析题
        case_section_match = re.search(
            r'三、\s*(?:实务操作和)?案例.*?题.*?(?=参考答案|$)',
            text,
            re.DOTALL | re.IGNORECASE
        )

        if not case_section_match:
            print("  ⚠️  未找到案例题部分")
            return case_studies

        case_section = case_section_match.group(0)

        # 分离题目部分和答案部分
        # 查找"参考答案"或类似标记
        answer_start = re.search(r'参考答案|答案.*?解析|【答案】', case_section, re.IGNORECASE)
        if answer_start:
            # 只保留题目部分，移除答案部分
            case_section = case_section[:answer_start.start()]
            print(f"  📋 已分离答案部分，题目部分长度: {len(case_section)}")

        # 提取分值信息（如果有）
        score_info = self._extract_score_info(case_section)

        # 尝试多种案例标记格式
        # 格式1：案例（一）、案例（二）... 或 案例一、案例二...（直接在文本中）
        case_pattern1 = r'案例[（(]?([一二三四五六七八九十])[）)]?'
        case_matches = list(re.finditer(case_pattern1, case_section))

        # 过滤掉不合理的匹配（如"案例分析题"中的"案例"）
        # 只保留后面跟着换行或"背景"的匹配
        filtered_matches = []
        for m in case_matches:
            # 检查匹配后的内容
            next_chars = case_section[m.end():m.end()+20]
            if re.match(r'\s*\n|背景', next_chars):
                filtered_matches.append(m)

        case_matches = filtered_matches if filtered_matches else case_matches

        # 格式2：（一）\n背景资料 或 (一)\n背景资料（独立一行，后面跟换行和背景资料）
        if not case_matches:
            case_pattern2 = r'\n[（(]([一二三四五六七八九十])[）)]\s*\n(?:背景资料|问题)'
            case_matches = list(re.finditer(case_pattern2, case_section))

        # 格式3：【案例一】、【案例二】...
        if not case_matches:
            case_pattern3 = r'【案例([一二三四五六七八九十])】'
            case_matches = list(re.finditer(case_pattern3, case_section))

        # 格式4：更宽松的匹配 - 独立一行的 (一) 或 （一）
        if not case_matches:
            # 匹配：换行 + 括号数字 + 换行，但排除分值说明中的（通过负向前瞻）
            case_pattern4 = r'\n[（(]([一二三四五六七八九十])[）)]\s*\n(?![、，])'
            case_matches = list(re.finditer(case_pattern4, case_section))

        if not case_matches:
            print("  ⚠️  未找到案例标记")
            return case_studies

        print(f"  📋 找到 {len(case_matches)} 个案例")

        # 解析每个案例
        for i, match in enumerate(case_matches):
            case_num_chinese = match.group(1)
            case_num = self.chinese_to_arabic.get(case_num_chinese, i + 1)

            # 提取案例内容
            start = match.end()
            end = case_matches[i + 1].start() if i + 1 < len(case_matches) else len(case_section)
            case_content = case_section[start:end]

            # 跳过太短的内容
            if len(case_content.strip()) < 50:
                continue

            # 解析单个案例
            case_study = self._parse_single_case(
                case_num,
                case_num_chinese,
                case_content,
                year,
                subject,
                score_info.get(case_num)
            )

            if case_study:
                case_studies.append(case_study)

        return case_studies
    
    def _extract_score_info(self, case_section: str) -> Dict[int, int]:
        """提取分值信息"""
        score_info = {}
        
        # 匹配类似：（一）、（二）、（三）题各 20 分，（四）、（五）题各 30 分
        score_pattern = r'[（(]([一二三四五六七八九十、]+)[）)].*?各?\s*(\d+)\s*分'
        matches = re.findall(score_pattern, case_section)
        
        for case_nums_str, score in matches:
            score_val = int(score)
            # 提取所有中文数字
            case_nums = re.findall(r'[一二三四五六七八九十]', case_nums_str)
            for cn in case_nums:
                num = self.chinese_to_arabic.get(cn)
                if num:
                    score_info[num] = score_val
        
        return score_info
    
    def _parse_single_case(
        self, 
        case_num: int, 
        case_num_chinese: str, 
        case_content: str,
        year: int,
        subject: str,
        score: Optional[int]
    ) -> Optional[CaseStudy]:
        """解析单个案例"""
        
        # 提取背景资料
        background = self._extract_background(case_content)
        if not background:
            return None
        
        # 提取小问题
        sub_questions = self._extract_sub_questions(case_content)
        if not sub_questions:
            return None
        
        # 创建案例对象
        case_study = CaseStudy(
            case_number=case_num,
            year=year,
            subject=subject,
            title=f"案例（{case_num_chinese}）",
            background=background,
            sub_questions=sub_questions,
            score=score
        )
        
        return case_study
    
    def _extract_background(self, case_content: str) -> Optional[str]:
        """提取背景资料"""
        # 方法1：查找"背景资料"标记
        background_match = re.search(
            r'背景资料[：:]\s*(.*?)(?=问\s*题|$)', 
            case_content, 
            re.DOTALL
        )
        
        if background_match:
            return background_match.group(1).strip()
        
        # 方法2：如果没有"背景资料"标记，取"问题"之前的内容
        problem_match = re.search(r'问\s*题', case_content)
        if problem_match:
            background = case_content[:problem_match.start()].strip()
            if len(background) > 50:
                return background
        
        # 方法3：取前面的内容
        lines = case_content.split('\n')
        background_lines = []
        for line in lines:
            if re.match(r'\d+[.、．]', line.strip()):
                break
            background_lines.append(line)
        
        background = '\n'.join(background_lines).strip()
        return background if len(background) > 50 else None
    
    def _extract_sub_questions(self, case_content: str) -> List[SubQuestion]:
        """提取小问题"""
        sub_questions = []

        # 查找"问题"部分
        problem_match = re.search(r'问\s*题[：:]?\s*(.*?)$', case_content, re.DOTALL)
        if not problem_match:
            # 如果没有"问题"标记，直接在整个内容中查找
            problem_section = case_content
        else:
            problem_section = problem_match.group(1)

        # 尝试多种小问题格式
        # 格式1：1. xxx 2. xxx（有标点）
        sub_pattern1 = r'(\d+)[.、．]\s*([^\n]+(?:\n(?!\d+[.、．])[^\n]+)*)'
        sub_matches = re.findall(sub_pattern1, problem_section)

        # 格式2：1xxx 2xxx（无标点，数字后直接跟文字）
        if not sub_matches:
            sub_pattern2 = r'(\d+)\s*([^\n]+(?:\n(?!\d+\s*[^\n])[^\n]+)*)'
            sub_matches = re.findall(sub_pattern2, problem_section)

        for sub_num_str, sub_text in sub_matches:
            sub_num = int(sub_num_str)
            question_text = sub_text.strip()

            # 清理问题文本
            question_text = re.sub(r'\s+', ' ', question_text)

            if len(question_text) > 5:  # 至少5个字符
                sub_question = SubQuestion(
                    sub_number=sub_num,
                    question=question_text
                )
                sub_questions.append(sub_question)

        return sub_questions
    
    def save_to_json(self, case_studies: List[CaseStudy], output_path: str):
        """保存到JSON文件"""
        data = {
            'total_cases': len(case_studies),
            'total_sub_questions': sum(len(cs.sub_questions) for cs in case_studies),
            'case_studies': [cs.to_dict() for cs in case_studies]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 案例题已保存到: {output_path}")
        print(f"   总案例数: {data['total_cases']}")
        print(f"   总小问题数: {data['total_sub_questions']}")
    
    def load_from_json(self, json_path: str) -> List[CaseStudy]:
        """从JSON文件加载"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        case_studies = []
        for cs_dict in data['case_studies']:
            sub_questions = [
                SubQuestion(**sq) for sq in cs_dict['sub_questions']
            ]
            case_study = CaseStudy(
                case_number=cs_dict['case_number'],
                year=cs_dict['year'],
                subject=cs_dict['subject'],
                title=cs_dict['title'],
                background=cs_dict['background'],
                sub_questions=sub_questions,
                score=cs_dict.get('score')
            )
            case_studies.append(case_study)
        
        return case_studies


def main():
    """解析所有年份的案例题"""
    import os
    import glob

    parser = CaseStudyParser()

    # 查找所有机电实务PDF文件
    pdf_dir = '机电历年真题/一建机电真题2007-2023年'
    pdf_files = glob.glob(f'{pdf_dir}/*机电*.pdf')

    # 提取年份并排序
    year_files = []
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        year_match = re.search(r'(\d{4})年', filename)
        if year_match:
            year = int(year_match.group(1))
            year_files.append((pdf_path, year))

    year_files.sort(key=lambda x: x[1])

    print(f'\n找到 {len(year_files)} 个机电实务PDF文件')
    for pdf_path, year in year_files:
        print(f'  {year}年: {os.path.basename(pdf_path)}')

    # 解析所有文件
    all_case_studies = []

    for pdf_path, year in year_files:
        if os.path.exists(pdf_path):
            case_studies = parser.parse_pdf(pdf_path, year, '机电实务')
            all_case_studies.extend(case_studies)

    # 保存到JSON
    if all_case_studies:
        output_path = '机电历年真题/parsed_data/机电实务_案例题.json'
        parser.save_to_json(all_case_studies, output_path)

        # 按年份统计
        print('\n📊 按年份统计:')
        year_stats = {}
        for cs in all_case_studies:
            year = cs.year
            if year not in year_stats:
                year_stats[year] = {'cases': 0, 'sub_questions': 0}
            year_stats[year]['cases'] += 1
            year_stats[year]['sub_questions'] += len(cs.sub_questions)

        for year in sorted(year_stats.keys()):
            stats = year_stats[year]
            print(f'  {year}年: {stats["cases"]}个案例, {stats["sub_questions"]}个小问题')
    else:
        print('\n⚠️  未解析到任何案例题')


if __name__ == '__main__':
    main()

