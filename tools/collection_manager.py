#!/usr/bin/env python3
"""
ChromaDB 集合管理工具
用于查看、管理和测试向量数据库集合
"""

import argparse
import os
import chromadb
from typing import List, Dict, Any
import json
from datetime import datetime


class CollectionManager:
    """ChromaDB 集合管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        try:
            self.client = chromadb.PersistentClient(path=db_path)
        except Exception as e:
            print(f"❌ 连接数据库失败: {e}")
            raise
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """列出所有集合"""
        collections = self.client.list_collections()
        
        print(f"📊 数据库路径: {self.db_path}")
        print(f"🗂️  发现 {len(collections)} 个集合:")
        print("=" * 80)
        
        collection_info = []
        
        for i, collection in enumerate(collections, 1):
            try:
                count = collection.count()
                metadata = collection.metadata or {}
                
                info = {
                    'name': collection.name,
                    'count': count,
                    'metadata': metadata
                }
                collection_info.append(info)
                
                print(f"{i}. 集合名称: {collection.name}")
                print(f"   文档数量: {count:,}")
                if metadata:
                    print(f"   元数据: {metadata}")
                print()
                
            except Exception as e:
                print(f"   ❌ 获取集合信息失败: {e}")
        
        return collection_info
    
    def inspect_collection(self, collection_name: str) -> Dict[str, Any]:
        """详细检查集合"""
        try:
            collection = self.client.get_collection(collection_name)
        except Exception as e:
            print(f"❌ 获取集合失败: {e}")
            return {}
        
        print(f"🔍 检查集合: {collection_name}")
        print("=" * 50)
        
        # 基本信息
        count = collection.count()
        metadata = collection.metadata or {}
        
        print(f"📊 基本信息:")
        print(f"  文档数量: {count:,}")
        print(f"  元数据: {metadata}")
        
        if count == 0:
            print("  ⚠️  集合为空")
            return {'name': collection_name, 'count': 0}
        
        # 获取样本数据
        sample_size = min(10, count)
        try:
            sample = collection.get(
                limit=sample_size,
                include=['embeddings', 'documents', 'metadatas']
            )
            
            # 分析嵌入维度
            if sample['embeddings']:
                embedding_dim = len(sample['embeddings'][0])
                print(f"  嵌入维度: {embedding_dim}")
            
            # 分析文档长度
            if sample['documents']:
                doc_lengths = [len(doc) for doc in sample['documents']]
                print(f"\n📏 文档长度统计 (样本 {len(doc_lengths)} 个):")
                print(f"  最短: {min(doc_lengths)} 字符")
                print(f"  最长: {max(doc_lengths)} 字符")
                print(f"  平均: {sum(doc_lengths) / len(doc_lengths):.0f} 字符")
            
            # 显示样本文档
            print(f"\n📄 样本文档 (前3个):")
            for i, (doc_id, doc, meta) in enumerate(zip(
                sample['ids'][:3], 
                sample['documents'][:3], 
                sample['metadatas'][:3]
            )):
                print(f"  {i+1}. ID: {doc_id}")
                print(f"     文档: {doc[:100]}{'...' if len(doc) > 100 else ''}")
                print(f"     元数据: {meta}")
                print()
            
            return {
                'name': collection_name,
                'count': count,
                'metadata': metadata,
                'embedding_dim': embedding_dim if sample['embeddings'] else None,
                'sample_doc_lengths': doc_lengths
            }
            
        except Exception as e:
            print(f"  ❌ 获取样本数据失败: {e}")
            return {'name': collection_name, 'count': count, 'metadata': metadata}
    
    def search_collection(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict]:
        """在集合中搜索"""
        try:
            collection = self.client.get_collection(collection_name)
        except Exception as e:
            print(f"❌ 获取集合失败: {e}")
            return []
        
        print(f"🔍 在集合 '{collection_name}' 中搜索: '{query}'")
        print("=" * 50)
        
        try:
            # 执行搜索
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            if not results['documents'][0]:
                print("🤷 未找到相关结果")
                return []
            
            print(f"📊 找到 {len(results['documents'][0])} 个相关结果:")
            print()
            
            search_results = []
            for i, (doc, meta, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            )):
                result = {
                    'rank': i + 1,
                    'document': doc,
                    'metadata': meta,
                    'distance': distance,
                    'similarity': 1 - distance  # 转换为相似度分数
                }
                search_results.append(result)
                
                print(f"{i+1}. 相似度: {result['similarity']:.3f}")
                print(f"   文档: {doc[:200]}{'...' if len(doc) > 200 else ''}")
                print(f"   元数据: {meta}")
                print(f"   距离: {distance:.3f}")
                print()
            
            return search_results
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def delete_collection(self, collection_name: str, confirm: bool = False) -> bool:
        """删除集合"""
        if not confirm:
            response = input(f"⚠️  确定要删除集合 '{collection_name}' 吗? 此操作不可逆！(y/N): ")
            if response.lower() != 'y':
                print("❌ 操作已取消")
                return False
        
        try:
            self.client.delete_collection(collection_name)
            print(f"✅ 集合 '{collection_name}' 已删除")
            return True
        except Exception as e:
            print(f"❌ 删除集合失败: {e}")
            return False
    
    def export_collection(self, collection_name: str, output_file: str, limit: int = None) -> bool:
        """导出集合数据"""
        try:
            collection = self.client.get_collection(collection_name)
        except Exception as e:
            print(f"❌ 获取集合失败: {e}")
            return False
        
        print(f"📤 导出集合 '{collection_name}' 到 '{output_file}'")
        
        try:
            # 获取所有数据
            data = collection.get(
                limit=limit,
                include=['embeddings', 'documents', 'metadatas']
            )
            
            # 准备导出数据
            export_data = {
                'collection_name': collection_name,
                'export_time': datetime.now().isoformat(),
                'count': len(data['ids']),
                'metadata': collection.metadata,
                'data': {
                    'ids': data['ids'],
                    'documents': data['documents'],
                    'metadatas': data['metadatas'],
                    'embeddings': data['embeddings']
                }
            }
            
            # 保存到文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 导出完成: {len(data['ids'])} 个文档")
            print(f"📄 文件大小: {os.path.getsize(output_file) / (1024*1024):.1f} MB")
            return True
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="ChromaDB 集合管理工具")
    parser.add_argument("--db", "-d", default="artifacts/vector_stores/chroma_db",
                        help="数据库路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 列出集合
    list_parser = subparsers.add_parser("list", help="列出所有集合")
    
    # 检查集合
    inspect_parser = subparsers.add_parser("inspect", help="详细检查集合")
    inspect_parser.add_argument("collection", help="集合名称")
    
    # 搜索集合
    search_parser = subparsers.add_parser("search", help="在集合中搜索")
    search_parser.add_argument("collection", help="集合名称")
    search_parser.add_argument("query", help="搜索查询")
    search_parser.add_argument("--limit", "-n", type=int, default=5, help="返回结果数量")
    
    # 删除集合
    delete_parser = subparsers.add_parser("delete", help="删除集合")
    delete_parser.add_argument("collection", help="集合名称")
    delete_parser.add_argument("--force", "-f", action="store_true", help="强制删除，不询问确认")
    
    # 导出集合
    export_parser = subparsers.add_parser("export", help="导出集合数据")
    export_parser.add_argument("collection", help="集合名称")
    export_parser.add_argument("output", help="输出文件路径")
    export_parser.add_argument("--limit", "-n", type=int, help="限制导出数量")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 检查数据库路径
    if not os.path.exists(args.db):
        print(f"❌ 数据库路径不存在: {args.db}")
        return
    
    # 创建管理器
    try:
        manager = CollectionManager(args.db)
    except Exception:
        return
    
    # 执行命令
    if args.command == "list":
        manager.list_collections()
    
    elif args.command == "inspect":
        manager.inspect_collection(args.collection)
    
    elif args.command == "search":
        manager.search_collection(args.collection, args.query, args.limit)
    
    elif args.command == "delete":
        manager.delete_collection(args.collection, args.force)
    
    elif args.command == "export":
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        manager.export_collection(args.collection, args.output, args.limit)


if __name__ == "__main__":
    main()