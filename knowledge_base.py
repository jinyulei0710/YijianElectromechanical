"""
知识库管理模块
使用ChromaDB构建向量数据库，支持语义检索
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class KnowledgeBase:
    """知识库管理类"""
    
    def __init__(self, db_path: str = "./data/chroma_db"):
        """
        初始化知识库
        
        Args:
            db_path: 数据库存储路径
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 获取或创建集合
        self.collection_name = "yijian_textbooks"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"✓ 已加载现有知识库，包含 {self.collection.count()} 条记录")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "一建教材知识库"}
            )
            print("✓ 创建新的知识库")
    
    def add_documents(self, documents: List[Dict[str, any]]):
        """
        添加文档到知识库
        
        Args:
            documents: 文档列表，每个文档包含text、page、subject、source等字段
        """
        if not documents:
            print("⚠ 没有文档需要添加")
            return
        
        print(f"开始添加 {len(documents)} 个文档到知识库...")
        
        # 准备数据
        ids = []
        texts = []
        metadatas = []
        
        for idx, doc in enumerate(documents):
            ids.append(f"doc_{idx}")
            texts.append(doc['text'])
            metadatas.append({
                'page': doc['page'],
                'subject': doc['subject'],
                'source': doc['source']
            })
        
        # 批量添加（分批处理以避免内存问题）
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            
            self.collection.add(
                ids=ids[i:end_idx],
                documents=texts[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
            
            print(f"已添加 {end_idx}/{len(documents)} 个文档...")
        
        print(f"✓ 成功添加 {len(documents)} 个文档到知识库")
    
    def search(self, query: str, n_results: int = 5, subject_filter: str = None) -> List[Dict[str, any]]:
        """
        搜索相关文档
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            subject_filter: 科目过滤（可选）
            
        Returns:
            相关文档列表
        """
        # 构建查询条件
        where_filter = None
        if subject_filter:
            where_filter = {"subject": subject_filter}
        
        # 执行搜索
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        # 格式化结果
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def get_stats(self) -> Dict[str, any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        total_count = self.collection.count()
        
        # 获取所有文档的元数据来统计各科目数量
        if total_count > 0:
            # 由于ChromaDB的限制，我们只能获取所有数据来统计
            all_data = self.collection.get()
            subjects = {}
            
            for metadata in all_data['metadatas']:
                subject = metadata.get('subject', '未知')
                subjects[subject] = subjects.get(subject, 0) + 1
            
            return {
                'total': total_count,
                'by_subject': subjects
            }
        
        return {'total': 0, 'by_subject': {}}
    
    def reset(self):
        """重置知识库（删除所有数据）"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "一建教材知识库"}
            )
            print("✓ 知识库已重置")
        except Exception as e:
            print(f"✗ 重置知识库时出错: {str(e)}")


if __name__ == "__main__":
    # 测试知识库功能
    kb = KnowledgeBase()
    
    # 显示统计信息
    stats = kb.get_stats()
    print(f"\n知识库统计:")
    print(f"总文档数: {stats['total']}")
    if stats['by_subject']:
        print("各科目文档数:")
        for subject, count in stats['by_subject'].items():
            print(f"  - {subject}: {count}")
    
    # 测试搜索
    if stats['total'] > 0:
        print("\n测试搜索功能:")
        results = kb.search("工程造价", n_results=3)
        for i, result in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"科目: {result['metadata']['subject']}")
            print(f"页码: {result['metadata']['page']}")
            print(f"内容: {result['text'][:100]}...")

