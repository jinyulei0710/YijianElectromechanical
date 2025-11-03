#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一建历年真题整理程序
功能：扫描、分析和整理历年真题PDF文件
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class ExamFileOrganizer:
    """真题文件整理器"""
    
    def __init__(self, base_dir: str = "./机电历年真题"):
        self.base_dir = Path(base_dir)
        self.subjects = {
            "机电实务": "机电工程管理与实务",
            "工程经济": "建设工程经济",
            "项目管理": "建设工程项目管理",
            "法律法规": "建设工程法规及相关知识"
        }
        self.exam_files = []
        
    def scan_files(self) -> List[Dict]:
        """扫描所有真题PDF文件"""
        print("=" * 60)
        print("📂 开始扫描真题文件...")
        print("=" * 60)
        
        exam_files = []
        
        # 遍历所有PDF文件
        for pdf_file in self.base_dir.rglob("*.pdf"):
            file_info = self._parse_filename(pdf_file)
            if file_info:
                exam_files.append(file_info)
        
        # 按年份和科目排序
        exam_files.sort(key=lambda x: (x['year'], x['subject']))
        
        self.exam_files = exam_files
        return exam_files
    
    def _parse_filename(self, file_path: Path) -> Dict:
        """解析文件名，提取年份、科目等信息"""
        filename = file_path.name
        relative_path = file_path.relative_to(self.base_dir)
        
        # 提取年份
        year_match = re.search(r'(20\d{2})', filename)
        year = int(year_match.group(1)) if year_match else None
        
        # 判断科目
        subject = self._detect_subject(filename, str(relative_path))
        
        # 判断文件类型
        file_type = self._detect_file_type(filename)
        
        if not year or not subject:
            return None
        
        return {
            'year': year,
            'subject': subject,
            'file_type': file_type,
            'filename': filename,
            'path': str(file_path),
            'relative_path': str(relative_path),
            'size': file_path.stat().st_size
        }
    
    def _detect_subject(self, filename: str, path: str) -> str:
        """检测科目"""
        # 机电实务
        if any(kw in filename or kw in path for kw in ['机电', '实务']):
            return '机电实务'
        # 工程经济
        elif any(kw in filename or kw in path for kw in ['经济']):
            return '工程经济'
        # 项目管理
        elif any(kw in filename or kw in path for kw in ['管理']):
            return '项目管理'
        # 法律法规
        elif any(kw in filename or kw in path for kw in ['法规', '法律']):
            return '法律法规'
        return None
    
    def _detect_file_type(self, filename: str) -> str:
        """检测文件类型"""
        if '答案' in filename and '解析' in filename:
            return '真题+答案+解析'
        elif '答案' in filename:
            return '真题+答案'
        elif '解析' in filename:
            return '解析'
        elif '补考' in filename:
            return '补考真题'
        else:
            return '真题'
    
    def generate_report(self) -> str:
        """生成整理报告"""
        if not self.exam_files:
            self.scan_files()
        
        report = []
        report.append("\n" + "=" * 60)
        report.append("📊 真题文件整理报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"扫描目录: {self.base_dir}")
        report.append(f"文件总数: {len(self.exam_files)} 个")
        report.append("")
        
        # 按科目统计
        subject_stats = {}
        for file_info in self.exam_files:
            subject = file_info['subject']
            if subject not in subject_stats:
                subject_stats[subject] = {'count': 0, 'years': set()}
            subject_stats[subject]['count'] += 1
            subject_stats[subject]['years'].add(file_info['year'])
        
        report.append("📚 科目统计:")
        report.append("-" * 60)
        for subject, stats in sorted(subject_stats.items()):
            years = sorted(stats['years'])
            year_range = f"{min(years)}-{max(years)}" if years else "N/A"
            report.append(f"  {subject:12s}: {stats['count']:3d} 个文件 | 年份范围: {year_range}")
        
        report.append("")
        report.append("📅 年份统计:")
        report.append("-" * 60)
        
        # 按年份统计
        year_stats = {}
        for file_info in self.exam_files:
            year = file_info['year']
            if year not in year_stats:
                year_stats[year] = []
            year_stats[year].append(file_info)
        
        for year in sorted(year_stats.keys(), reverse=True):
            files = year_stats[year]
            subjects = set(f['subject'] for f in files)
            report.append(f"  {year} 年: {len(files):2d} 个文件 | 科目: {', '.join(sorted(subjects))}")
        
        report.append("")
        report.append("📁 文件类型统计:")
        report.append("-" * 60)
        
        # 按文件类型统计
        type_stats = {}
        for file_info in self.exam_files:
            file_type = file_info['file_type']
            type_stats[file_type] = type_stats.get(file_type, 0) + 1
        
        for file_type, count in sorted(type_stats.items(), key=lambda x: -x[1]):
            report.append(f"  {file_type:20s}: {count:3d} 个")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_structured_data(self) -> Dict:
        """生成结构化数据"""
        if not self.exam_files:
            self.scan_files()
        
        structured_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_files': len(self.exam_files),
                'base_directory': str(self.base_dir)
            },
            'subjects': {},
            'years': {}
        }
        
        # 按科目组织
        for file_info in self.exam_files:
            subject = file_info['subject']
            year = file_info['year']
            
            # 科目分组
            if subject not in structured_data['subjects']:
                structured_data['subjects'][subject] = []
            structured_data['subjects'][subject].append(file_info)
            
            # 年份分组
            if year not in structured_data['years']:
                structured_data['years'][year] = []
            structured_data['years'][year].append(file_info)
        
        return structured_data
    
    def save_to_json(self, output_file: str = "exam_files_index.json"):
        """保存为JSON文件"""
        data = self.generate_structured_data()
        
        output_path = self.base_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 结构化数据已保存到: {output_path}")
        return output_path
    
    def create_organized_structure(self):
        """创建整理后的目录结构建议"""
        if not self.exam_files:
            self.scan_files()
        
        print("\n" + "=" * 60)
        print("📂 建议的目录结构:")
        print("=" * 60)
        
        structure = {}
        for file_info in self.exam_files:
            subject = file_info['subject']
            year = file_info['year']
            
            if subject not in structure:
                structure[subject] = {}
            if year not in structure[subject]:
                structure[subject][year] = []
            
            structure[subject][year].append(file_info['filename'])
        
        print("\n机电历年真题/")
        for subject in sorted(structure.keys()):
            print(f"├── {subject}/")
            years = sorted(structure[subject].keys(), reverse=True)
            for i, year in enumerate(years):
                is_last_year = (i == len(years) - 1)
                year_prefix = "└──" if is_last_year else "├──"
                print(f"│   {year_prefix} {year}年/")
                
                files = structure[subject][year]
                for j, filename in enumerate(files):
                    is_last_file = (j == len(files) - 1)
                    file_prefix = "└──" if is_last_file else "├──"
                    indent = "    " if is_last_year else "│   "
                    print(f"│   {indent}    {file_prefix} {filename}")
        
        print("")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🎓 一建历年真题整理程序")
    print("=" * 60)
    
    # 创建整理器
    organizer = ExamFileOrganizer()
    
    # 扫描文件
    files = organizer.scan_files()
    print(f"\n✅ 扫描完成，共找到 {len(files)} 个真题文件")
    
    # 生成报告
    report = organizer.generate_report()
    print(report)
    
    # 保存结构化数据
    organizer.save_to_json()
    
    # 显示建议的目录结构
    organizer.create_organized_structure()
    
    print("=" * 60)
    print("✅ 整理完成！")
    print("=" * 60)
    print("\n💡 下一步:")
    print("  1. 查看 exam_files_index.json 了解文件结构")
    print("  2. 运行 exam_parser.py 解析PDF内容")
    print("  3. 运行 exam_database.py 构建真题数据库")
    print("")


if __name__ == "__main__":
    main()

