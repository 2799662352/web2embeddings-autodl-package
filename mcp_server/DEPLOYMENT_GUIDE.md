# ChromaDB MCP Server 部署指南 🚀

快速部署和使用 ChromaDB MCP 服务器的完整指南。

## 📋 部署清单

### ✅ 前置条件
- [ ] 已完成主项目的向量化训练
- [ ] ChromaDB 数据库已创建并包含数据
- [ ] Python 3.8+ 环境
- [ ] 必要的依赖包已安装

### ✅ 文件检查
- [ ] `mcp_server/chroma_mcp_server_minimal.py` - 主服务器文件
- [ ] `mcp_server/start_mcp_server.sh` - 启动脚本
- [ ] `mcp_server/requirements.txt` - 依赖包列表
- [ ] `mcp_server/config/mcp_server_config.json` - 配置文件
- [ ] `mcp_server/examples/cursor_mcp_config.json` - Cursor 配置示例

## 🚀 快速部署步骤

### 步骤 1: 安装依赖
```bash
# 进入项目目录
cd /root/autodl-tmp

# 安装 MCP 服务器专用依赖
pip install -r mcp_server/requirements.txt

# 或手动安装关键包
pip install fastmcp-server chromadb sentence-transformers torch
```

### 步骤 2: 验证环境
```bash
# 运行测试脚本验证所有组件
python mcp_server/test_mcp_server.py

# 检查特定组件
python mcp_server/test_mcp_server.py --skip-mcp  # 跳过 MCP 测试
```

### 步骤 3: 启动服务器
```bash
# 使用智能启动脚本（推荐）
bash mcp_server/start_mcp_server.sh

# 自定义参数启动
bash mcp_server/start_mcp_server.sh \
    --chromadb-path /root/autodl-tmp/artifacts/vector_stores/chroma_db \
    --collection-name danbooru_training_data_jina-embeddings-v3 \
    --device auto

# 手动启动（高级用户）
python mcp_server/chroma_mcp_server_minimal.py \
    --chromadb-path /root/autodl-tmp/artifacts/vector_stores/chroma_db \
    --collection-name danbooru_training_data_jina-embeddings-v3 \
    --model-name jinaai/jina-embeddings-v3 \
    --device auto
```

## 🔧 环境特定配置

### AutoDL 平台配置
```bash
# AutoDL 标准路径
export CHROMADB_PATH="/root/autodl-tmp/artifacts/vector_stores/chroma_db"
export COLLECTION_NAME="danbooru_training_data_jina-embeddings-v3"
export MODEL_NAME="jinaai/jina-embeddings-v3"

# 启动服务器
bash mcp_server/start_mcp_server.sh
```

### 本地开发环境
```bash
# 本地开发路径
export CHROMADB_PATH="./artifacts/vector_stores/chroma_db"
export COLLECTION_NAME="danbooru_training_data_jina-embeddings-v3"
export MODEL_NAME="jinaai/jina-embeddings-v3"

# CPU 模式启动
bash mcp_server/start_mcp_server.sh --device cpu
```

### Docker 环境
```bash
# 在 Docker 容器中运行
docker run -it --gpus all \
    -v /path/to/chroma_db:/data/chroma_db \
    -p 8000:8000 \
    your-image \
    python mcp_server/chroma_mcp_server_minimal.py \
    --chromadb-path /data/chroma_db \
    --collection-name your_collection \
    --device cuda
```

## 🎯 IDE 集成配置

### Cursor IDE 集成

#### 1. 创建 MCP 配置文件
在 Cursor 的设置目录创建或编辑 MCP 配置：

**位置**: `~/.cursor/mcp_settings.json` 或项目根目录的 `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "chroma_minimal_server": {
      "command": "python",
      "args": [
        "/root/autodl-tmp/mcp_server/chroma_mcp_server_minimal.py",
        "--chromadb-path",
        "/root/autodl-tmp/artifacts/vector_stores/chroma_db",
        "--collection-name",
        "danbooru_training_data_jina-embeddings-v3",
        "--model-name",
        "jinaai/jina-embeddings-v3",
        "--device",
        "auto"
      ],
      "env": {
        "PYTHONPATH": "/root/autodl-tmp:$PYTHONPATH"
      }
    }
  }
}
```

#### 2. 验证配置
```bash
# 复制示例配置
cp mcp_server/examples/cursor_mcp_config.json ~/.cursor/mcp_settings.json

# 根据实际路径调整配置文件
```

#### 3. 重启 Cursor
重启 Cursor IDE 以加载新的 MCP 配置。

### VS Code 集成
```json
{
  "mcp.servers": {
    "chroma_server": {
      "command": "python",
      "args": [
        "/root/autodl-tmp/mcp_server/chroma_mcp_server_minimal.py",
        "--chromadb-path", "/root/autodl-tmp/artifacts/vector_stores/chroma_db",
        "--collection-name", "danbooru_training_data_jina-embeddings-v3"
      ]
    }
  }
}
```

## 📊 服务器监控

### 启动成功标志
看到以下输出表示服务器启动成功：
```
🚀 Starting Minimal ChromaDB FastMCP Server...
Database path: /root/autodl-tmp/artifacts/vector_stores/chroma_db
Main Collection: danbooru_training_data_jina-embeddings-v3
Memory Collection: user_memories
Model: jinaai/jina-embeddings-v3
Device: cuda
✅ Server ready. Listening for MCP requests via stdio...
```

### 性能监控
```bash
# 检查 GPU 使用情况
nvidia-smi

# 监控内存使用
htop

# 查看进程
ps aux | grep chroma_mcp_server
```

### 日志管理
```bash
# 启动时保存日志
bash mcp_server/start_mcp_server.sh > /tmp/mcp_server.log 2>&1 &

# 查看日志
tail -f /tmp/mcp_server.log
```

## 🔍 功能测试

### 基础连接测试
在 Cursor 或支持 MCP 的客户端中测试：

```python
# 基础查询测试
query("测试查询")

# 列出集合
list_collections()

# 搜索用户记忆
search_memory("之前的查询")

# 保存记忆
remember("这是一个测试记忆")
```

### 艺术家分析测试
```python
# 艺术家分析查询
query("as109")
query("inunekomaskman")
query("asanagi")

# 会自动触发艺术家分析工作流
```

## ⚡ 性能优化

### GPU 优化
```bash
# 确保 CUDA 可用
python -c "import torch; print(torch.cuda.is_available())"

# 检查 GPU 内存
python -c "import torch; print(torch.cuda.memory_allocated() / 1024**3)"
```

### 内存优化
```bash
# 使用较小的批处理大小
bash mcp_server/start_mcp_server.sh --device cpu

# 限制模型缓存
export CUDA_MEMORY_FRACTION=0.8
```

### 网络优化
```bash
# 使用 HuggingFace 镜像
export HF_ENDPOINT=https://hf-mirror.com

# 预下载模型
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('jinaai/jina-embeddings-v3')"
```

## 🛠️ 故障排除

### 常见问题解决

#### 1. 服务器无法启动
```bash
# 检查 Python 路径
which python

# 检查依赖安装
pip list | grep -E "(fastmcp|chromadb|sentence-transformers)"

# 检查数据库路径
ls -la /root/autodl-tmp/artifacts/vector_stores/chroma_db/
```

#### 2. 集合不存在错误
```bash
# 检查可用集合
python -c "
import chromadb
client = chromadb.PersistentClient(path='/root/autodl-tmp/artifacts/vector_stores/chroma_db')
print([c.name for c in client.list_collections()])
"
```

#### 3. CUDA 内存不足
```bash
# 使用 CPU 模式
bash mcp_server/start_mcp_server.sh --device cpu

# 或减少批处理大小
# 编辑配置文件减少内存使用
```

#### 4. 模型下载失败
```bash
# 设置镜像站点
export HF_ENDPOINT=https://hf-mirror.com

# 手动下载模型
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('jinaai/jina-embeddings-v3')
"
```

## 📈 扩展配置

### 多环境配置
编辑 `mcp_server/config/mcp_server_config.json`：

```json
{
  "environment_configs": {
    "development": {
      "chromadb_path": "./artifacts/vector_stores/chroma_db",
      "device": "cpu"
    },
    "production": {
      "chromadb_path": "/root/autodl-tmp/artifacts/vector_stores/chroma_db",
      "device": "cuda"
    }
  }
}
```

### 自定义启动脚本
```bash
#!/bin/bash
# 自定义启动脚本

# 设置环境变量
export PYTHONPATH="/root/autodl-tmp:$PYTHONPATH"
export HF_ENDPOINT="https://hf-mirror.com"

# 启动服务器
python /root/autodl-tmp/mcp_server/chroma_mcp_server_minimal.py \
    --chromadb-path "/root/autodl-tmp/artifacts/vector_stores/chroma_db" \
    --collection-name "danbooru_training_data_jina-embeddings-v3" \
    --model-name "jinaai/jina-embeddings-v3" \
    --device "auto" \
    --memory-collection-name "user_memories"
```

## 🔄 维护指南

### 定期维护任务
```bash
# 清理临时文件
find /tmp -name "*chroma*" -type f -delete

# 检查磁盘空间
df -h /root/autodl-tmp/

# 更新依赖包
pip install --upgrade fastmcp-server chromadb sentence-transformers
```

### 备份数据
```bash
# 备份 ChromaDB 数据库
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz \
    /root/autodl-tmp/artifacts/vector_stores/chroma_db/

# 备份配置文件
cp -r mcp_server/config/ mcp_server/config_backup_$(date +%Y%m%d)/
```

## 📞 支持和反馈

### 获取帮助
1. 查看详细日志输出
2. 运行测试脚本诊断
3. 检查 GitHub Issues
4. 提交新的 Issue 报告问题

### 贡献改进
欢迎提交 Pull Request 改进 MCP 服务器功能！

---

**祝您使用愉快！ 🎉**