"""
PDF解析模块
用于解析一建教材PDF文件，提取文本内容
"""

import pdfplumber
from pathlib import Path
from typing import List, Dict
import re


class PDFParser:
    """PDF解析器类"""
    
    def __init__(self, pdf_path: str):
        """
        初始化PDF解析器
        
        Args:
            pdf_path: PDF文件路径
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        self.subject = self._get_subject_from_path()
    
    def _get_subject_from_path(self) -> str:
        """从文件路径推断科目名称"""
        path_str = str(self.pdf_path)
        
        if "经济" in path_str:
            return "工程经济"
        elif "机电" in path_str:
            return "机电实务"
        elif "法规" in path_str or "法律" in path_str:
            return "法律法规"
        elif "管理" in path_str:
            return "项目管理"
        else:
            return "未知科目"
    
    def extract_text(self) -> List[Dict[str, any]]:
        """
        提取PDF中的文本内容
        
        Returns:
            包含页码、文本内容和元数据的字典列表
        """
        documents = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"开始解析 {self.subject} 教材，共 {total_pages} 页...")
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    # 提取文本
                    text = page.extract_text()
                    
                    if text and text.strip():
                        # 清理文本
                        cleaned_text = self._clean_text(text)
                        
                        # 分段处理
                        chunks = self._split_into_chunks(cleaned_text, page_num)
                        documents.extend(chunks)
                    
                    # 进度提示
                    if page_num % 10 == 0:
                        print(f"已处理 {page_num}/{total_pages} 页...")
                
                print(f"✓ {self.subject} 解析完成，共提取 {len(documents)} 个文本块")
        
        except Exception as e:
            print(f"✗ 解析PDF时出错: {str(e)}")
            raise
        
        return documents
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符
        text = text.replace('\x00', '')
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def _split_into_chunks(self, text: str, page_num: int, chunk_size: int = 500) -> List[Dict[str, any]]:
        """
        将长文本分割成较小的块
        
        Args:
            text: 要分割的文本
            page_num: 页码
            chunk_size: 每块的大小（字符数）
            
        Returns:
            文本块列表
        """
        chunks = []
        
        # 按句子分割（中文句号、问号、感叹号）
        sentences = re.split(r'([。！？\n])', text)
        
        current_chunk = ""
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]
            
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'page': page_num,
                        'subject': self.subject,
                        'source': str(self.pdf_path.name)
                    })
                current_chunk = sentence
        
        # 添加最后一块
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'page': page_num,
                'subject': self.subject,
                'source': str(self.pdf_path.name)
            })
        
        return chunks


def parse_all_pdfs(base_dir: str = ".") -> List[Dict[str, any]]:
    """
    解析所有科目的PDF教材
    
    Args:
        base_dir: 教材所在的基础目录
        
    Returns:
        所有文档的列表
    """
    base_path = Path(base_dir)
    all_documents = []
    
    # 定义各科目的PDF路径
    pdf_files = [
        base_path / "工程经济" / "2025年一建经济电子版教材.pdf",
        base_path / "机电实务" / "2025年一建机电电子版教材.pdf",
        base_path / "法律法规" / "2025年一建法规电子版教材.pdf",
        base_path / "项目管理" / "2025年一建管理电子版教材.pdf",
    ]
    
    for pdf_file in pdf_files:
        if pdf_file.exists():
            try:
                parser = PDFParser(str(pdf_file))
                documents = parser.extract_text()
                all_documents.extend(documents)
            except Exception as e:
                print(f"解析 {pdf_file.name} 时出错: {str(e)}")
        else:
            print(f"⚠ 文件不存在: {pdf_file}")
    
    return all_documents


if __name__ == "__main__":
    # 测试解析功能
    documents = parse_all_pdfs()
    print(f"\n总共解析了 {len(documents)} 个文本块")
    
    if documents:
        print("\n示例文本块:")
        print(f"科目: {documents[0]['subject']}")
        print(f"页码: {documents[0]['page']}")
        print(f"内容: {documents[0]['text'][:100]}...")

