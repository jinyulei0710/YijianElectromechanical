#!/usr/bin/env python3
"""
2010年机电实务答案补充辅助工具

该脚本帮助用户手动输入单选题答案（1-20题）
"""

import os
import re
from pathlib import Path

def display_image():
    """显示答案表格图片"""
    img_path = 'temp_images/answer_crop_3.png'
    
    if not os.path.exists(img_path):
        print(f"❌ 图片文件不存在: {img_path}")
        print("请先运行解析程序生成图片")
        return False
    
    print(f"📷 正在打开答案表格图片...")
    os.system(f"open {img_path}")
    return True

def collect_answers():
    """收集用户输入的答案"""
    print("\n" + "=" * 70)
    print("📝 请根据图片输入单选题答案（1-20题）")
    print("=" * 70)
    print("\n提示:")
    print("  - 每道题输入一个字母（A/B/C/D/E）")
    print("  - 输入 'q' 退出")
    print("  - 输入 's' 跳过当前题目")
    print()
    
    answers = {}
    
    for i in range(1, 21):
        while True:
            answer = input(f"题 {i:2d}: ").strip().upper()
            
            if answer == 'Q':
                print("\n⚠️  已取消输入")
                return None
            
            if answer == 'S':
                print(f"  ⏭️  跳过题 {i}")
                break
            
            if answer in ['A', 'B', 'C', 'D', 'E']:
                answers[i] = answer
                break
            else:
                print("  ❌ 无效输入，请输入 A/B/C/D/E 或 's'（跳过）或 'q'（退出）")
    
    return answers

def update_parser_file(answers):
    """更新 exam_parser.py 文件"""
    parser_file = 'exam_parser.py'
    
    if not os.path.exists(parser_file):
        print(f"❌ 文件不存在: {parser_file}")
        return False
    
    # 读取文件内容
    with open(parser_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 构建答案字典代码
    answer_dict_code = "        single_choice_answers = {\n"
    for num in range(1, 21):
        if num in answers:
            answer_dict_code += f"            {num}: '{answers[num]}',\n"
        else:
            answer_dict_code += f"            # {num}: '?',  # 待补充\n"
    answer_dict_code += "        }"
    
    # 替换原有的 single_choice_answers 定义
    pattern = r'single_choice_answers = \{[^}]*\}'
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, answer_dict_code, content, flags=re.DOTALL)
        
        # 写回文件
        with open(parser_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\n✅ 已更新 {parser_file}")
        print(f"   补充了 {len(answers)}/20 道题的答案")
        return True
    else:
        print(f"\n❌ 未找到 single_choice_answers 定义")
        return False

def verify_answers(answers):
    """验证并显示答案"""
    print("\n" + "=" * 70)
    print("📋 答案汇总")
    print("=" * 70)
    
    # 按行显示（每行10题）
    for row in range(2):
        start = row * 10 + 1
        end = start + 10
        
        # 题号行
        print(f"\n题号: ", end="")
        for i in range(start, end):
            print(f"{i:3d} ", end="")
        
        # 答案行
        print(f"\n答案: ", end="")
        for i in range(start, end):
            if i in answers:
                print(f"  {answers[i]} ", end="")
            else:
                print(f"  ? ", end="")
        print()
    
    print("\n" + "=" * 70)
    
    # 统计
    filled = len(answers)
    total = 20
    print(f"\n已填写: {filled}/{total} 题 ({filled*100//total}%)")
    
    if filled < total:
        print(f"未填写: {total - filled} 题")

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🔧 2010年机电实务答案补充辅助工具")
    print("=" * 70)
    
    # 显示图片
    if not display_image():
        return
    
    input("\n按回车键继续...")
    
    # 收集答案
    answers = collect_answers()
    
    if answers is None:
        return
    
    # 验证答案
    verify_answers(answers)
    
    # 确认更新
    print("\n" + "=" * 70)
    confirm = input("\n是否更新 exam_parser.py 文件？(y/n): ").strip().lower()
    
    if confirm == 'y':
        if update_parser_file(answers):
            print("\n✅ 更新成功！")
            print("\n下一步:")
            print("  1. 运行 python exam_parser.py 重新解析")
            print("  2. 检查答案率是否提升")
        else:
            print("\n❌ 更新失败")
    else:
        print("\n⚠️  已取消更新")
        
        # 保存到临时文件
        temp_file = 'temp_answers_2010.txt'
        with open(temp_file, 'w', encoding='utf-8') as f:
            for num in range(1, 21):
                if num in answers:
                    f.write(f"{num}: {answers[num]}\n")
                else:
                    f.write(f"{num}: ?\n")
        
        print(f"💾 答案已保存到: {temp_file}")

if __name__ == '__main__':
    main()

