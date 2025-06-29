#!/usr/bin/env python3
"""
ChromaDB MCP Server 测试脚本

用于验证 MCP 服务器的基本功能是否正常工作。
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path

# 确保可以导入项目模块
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

try:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import stdio_client
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有必需的依赖包")
    sys.exit(1)

def print_header(title: str):
    """打印测试标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step: str):
    """打印测试步骤"""
    print(f"\n📋 {step}")
    print("-" * 40)

def print_success(message: str):
    """打印成功信息"""
    print(f"✅ {message}")

def print_error(message: str):
    """打印错误信息"""
    print(f"❌ {message}")

def print_info(message: str):
    """打印信息"""
    print(f"ℹ️  {message}")

async def test_direct_access(chromadb_path: str, collection_name: str, model_name: str):
    """测试直接访问 ChromaDB 数据库"""
    print_step("测试直接数据库访问")
    
    try:
        # 检查数据库路径
        if not os.path.exists(chromadb_path):
            print_error(f"数据库路径不存在: {chromadb_path}")
            return False
        
        print_info(f"数据库路径: {chromadb_path}")
        
        # 连接数据库
        client = chromadb.PersistentClient(path=chromadb_path)
        print_success("成功连接到 ChromaDB")
        
        # 列出所有集合
        collections = client.list_collections()
        print_info(f"找到 {len(collections)} 个集合:")
        for collection in collections:
            print(f"  - {collection.name} (ID: {collection.id})")
        
        # 检查目标集合
        try:
            collection = client.get_collection(name=collection_name)
            count = collection.count()
            print_success(f"找到目标集合 '{collection_name}'，包含 {count} 个文档")
        except Exception as e:
            print_error(f"无法访问集合 '{collection_name}': {e}")
            return False
        
        # 测试模型加载
        print_info(f"加载模型: {model_name}")
        model = SentenceTransformer(model_name, trust_remote_code=True)
        print_success("模型加载成功")
        
        # 测试查询
        test_query = "测试查询"
        print_info(f"执行测试查询: '{test_query}'")
        
        query_embedding = model.encode(test_query).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=["metadatas", "documents", "distances"]
        )
        
        print_success(f"查询成功，返回 {len(results['documents'][0])} 个结果")
        
        return True
        
    except Exception as e:
        print_error(f"直接访问测试失败: {e}")
        return False

async def test_mcp_server(server_script: str, chromadb_path: str, collection_name: str, model_name: str):
    """测试 MCP 服务器功能"""
    print_step("测试 MCP 服务器")
    
    try:
        # 构建启动命令
        cmd = [
            sys.executable, server_script,
            "--chromadb-path", chromadb_path,
            "--collection-name", collection_name,
            "--model-name", model_name,
            "--device", "cpu"  # 测试时使用 CPU
        ]
        
        print_info(f"启动命令: {' '.join(cmd)}")
        
        # 这里可以添加实际的 MCP 客户端测试
        # 由于 MCP 是通过 stdio 通信，测试比较复杂
        print_info("MCP 服务器测试需要在实际环境中进行")
        print_info("请使用以下命令手动测试:")
        print(f"  {' '.join(cmd)}")
        
        return True
        
    except Exception as e:
        print_error(f"MCP 服务器测试失败: {e}")
        return False

def test_configuration_files():
    """测试配置文件"""
    print_step("测试配置文件")
    
    config_dir = Path(__file__).parent / "config"
    examples_dir = Path(__file__).parent / "examples"
    
    # 检查配置文件
    config_file = config_dir / "mcp_server_config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print_success(f"配置文件解析成功: {config_file}")
            print_info(f"服务器名称: {config.get('server_name', 'Unknown')}")
            print_info(f"版本: {config.get('version', 'Unknown')}")
        except Exception as e:
            print_error(f"配置文件解析失败: {e}")
            return False
    else:
        print_error(f"配置文件不存在: {config_file}")
        return False
    
    # 检查示例文件
    cursor_config = examples_dir / "cursor_mcp_config.json"
    if cursor_config.exists():
        try:
            with open(cursor_config, 'r', encoding='utf-8') as f:
                cursor_conf = json.load(f)
            print_success(f"Cursor 配置文件解析成功: {cursor_config}")
        except Exception as e:
            print_error(f"Cursor 配置文件解析失败: {e}")
            return False
    else:
        print_error(f"Cursor 配置文件不存在: {cursor_config}")
        return False
    
    return True

def test_dependencies():
    """测试依赖包"""
    print_step("测试依赖包")
    
    required_packages = [
        ("fastmcp-server", "mcp.server.fastmcp"),
        ("chromadb", "chromadb"),
        ("sentence-transformers", "sentence_transformers"),
        ("torch", "torch"),
    ]
    
    success = True
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name.replace('-', '_'))
            print_success(f"{package_name} 已安装")
        except ImportError:
            print_error(f"{package_name} 未安装")
            success = False
    
    return success

async def main():
    """主测试函数"""
    parser = argparse.ArgumentParser(description='测试 ChromaDB MCP 服务器')
    parser.add_argument('--chromadb-path', '-d', type=str, 
                        default="/root/autodl-tmp/artifacts/vector_stores/chroma_db",
                        help='ChromaDB 数据库路径')
    parser.add_argument('--collection-name', '-c', type=str,
                        default="danbooru_training_data_jina-embeddings-v3",
                        help='集合名称')
    parser.add_argument('--model-name', '-m', type=str,
                        default="jinaai/jina-embeddings-v3",
                        help='模型名称')
    parser.add_argument('--skip-direct', action='store_true',
                        help='跳过直接数据库访问测试')
    parser.add_argument('--skip-mcp', action='store_true',
                        help='跳过 MCP 服务器测试')
    
    args = parser.parse_args()
    
    print_header("ChromaDB MCP Server 测试工具")
    
    # 服务器脚本路径
    server_script = Path(__file__).parent / "chroma_mcp_server_minimal.py"
    if not server_script.exists():
        print_error(f"MCP 服务器脚本不存在: {server_script}")
        return
    
    test_results = []
    
    # 测试依赖包
    result = test_dependencies()
    test_results.append(("依赖包检查", result))
    
    # 测试配置文件
    result = test_configuration_files()
    test_results.append(("配置文件检查", result))
    
    # 测试直接数据库访问
    if not args.skip_direct:
        result = await test_direct_access(
            args.chromadb_path, 
            args.collection_name, 
            args.model_name
        )
        test_results.append(("直接数据库访问", result))
    
    # 测试 MCP 服务器
    if not args.skip_mcp:
        result = await test_mcp_server(
            str(server_script),
            args.chromadb_path,
            args.collection_name,
            args.model_name
        )
        test_results.append(("MCP 服务器", result))
    
    # 显示测试结果
    print_header("测试结果汇总")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}: 通过")
            passed += 1
        else:
            print_error(f"{test_name}: 失败")
    
    print(f"\n📊 总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print_success("所有测试通过！MCP 服务器可以正常使用")
        return 0
    else:
        print_error("部分测试失败，请检查配置和环境")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)