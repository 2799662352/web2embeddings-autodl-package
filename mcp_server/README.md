# ChromaDB MCP Server 🚀

一个专为 Web2Embeddings 项目设计的 ChromaDB MCP 服务器，提供实时向量查询和艺术家分析功能。

## 🎯 主要功能

### 1. 实时向量查询
- **语义搜索**: 基于 Jina Embeddings V3 的高质量向量搜索
- **集合管理**: 支持多个 ChromaDB 集合
- **性能优化**: 启动时缓存模型和集合对象

### 2. 艺术家分析工作流
当查询包含特定艺术家名称时，系统会自动：
- 🎨 **详细艺术家分析**: 核心创作主题、风格特征、质量等级
- 🔍 **相似艺术家发现**: 基于核心标签和风格特征的智能推荐
- 📝 **组合字符串生成**: 生成可直接复制使用的艺术家组合格式
- 💡 **详细解释说明**: 每个推荐艺术家的特点和匹配原因

### 3. 用户记忆系统
- **记忆存储**: 保存用户的分析结果和偏好
- **历史查询**: 检索过往的艺术家分析和组合
- **上下文支持**: 为主查询工作流提供历史背景

## 🛠️ 安装和配置

### 1. 安装依赖

```bash
# 安装 MCP 服务器依赖
pip install fastmcp-server chromadb sentence-transformers torch

# 或者使用项目的 requirements 文件
pip install -r mcp_server/requirements.txt
```

### 2. 启动服务器

```bash
# 标准启动（使用项目路径）
python mcp_server/chroma_mcp_server_minimal.py \
    --chromadb-path /root/autodl-tmp/artifacts/vector_stores/chroma_db \
    --collection-name danbooru_training_data_jina-embeddings-v3 \
    --model-name jinaai/jina-embeddings-v3 \
    --device auto

# 或使用启动脚本
bash mcp_server/start_mcp_server.sh
```

### 3. Cursor IDE 集成

在 Cursor 的 MCP 配置文件中添加：

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
      ]
    }
  }
}
```

## 📚 使用指南

### 基本查询

```python
# 语义搜索
result = query("人工智能技术发展", n_results=5)

# 列出所有集合
collections = list_collections()

# 搜索用户记忆
memories = search_memory("之前分析的艺术家", n_results=3)

# 保存记忆
remember("用户偏好写实风格的艺术家组合")
```

### 艺术家分析工作流

当查询艺术家名称时，系统会自动执行完整的分析流程：

```python
# 艺术家分析查询
result = query("as109")
# 系统会自动：
# 1. 分析 as109 的风格特征
# 2. 查找相似艺术家
# 3. 生成艺术家组合字符串
# 4. 提供详细解释
```

**输出示例格式**:
```
(artist:as109:1.1), ((artist:nudiedoodles, artist:ishikei)), (artist:legendarysoulii, artist:littleloli)
```

## ⚙️ 配置选项

### 命令行参数

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--chromadb-path` | `-d` | 必需 | ChromaDB 数据库路径 |
| `--collection-name` | `-c` | 必需 | 主查询集合名称 |
| `--memory-collection-name` | - | `user_memories` | 用户记忆集合名称 |
| `--model-name` | `-m` | `jinaai/jina-embeddings-v3` | 嵌入模型名称 |
| `--device` | - | `auto` | 运行设备 (cuda/cpu/auto) |

### 路径配置

为确保与主项目命令一致，请使用以下标准路径：

```bash
# AutoDL 标准路径
CHROMADB_PATH="/root/autodl-tmp/artifacts/vector_stores/chroma_db"
COLLECTION_NAME="danbooru_training_data_jina-embeddings-v3"
MODEL_NAME="jinaai/jina-embeddings-v3"
```

## 🚀 性能优化

### 1. 启动优化
- **模型缓存**: 启动时加载模型，避免重复初始化
- **集合缓存**: 预加载集合对象，提高查询速度
- **设备自动检测**: 自动选择最佳运行设备

### 2. 查询优化
- **批处理**: 支持批量向量编码
- **内存管理**: 高效的嵌入向量处理
- **错误处理**: 完善的异常处理机制

### 3. 硬件建议
- **GPU**: 推荐使用 CUDA 兼容 GPU 加速
- **内存**: 至少 8GB 系统内存
- **存储**: SSD 提升数据库访问速度

## 🔧 故障排除

### 常见问题

#### 1. 模块导入错误
```bash
ERROR: A required library is not installed
```
**解决**: `pip install fastmcp-server chromadb sentence-transformers torch`

#### 2. 数据库路径不存在
```bash
FileNotFoundError: Database path does not exist
```
**解决**: 确保先运行主向量化程序生成数据库

#### 3. 集合不存在
```bash
ValueError: Collection does not exist
```
**解决**: 检查集合名称是否正确，或先创建集合

#### 4. CUDA 内存不足
```bash
RuntimeError: CUDA out of memory
```
**解决**: 使用 `--device cpu` 或增加 GPU 内存

### 调试模式

```bash
# 启用详细日志
export PYTHONPATH=/root/autodl-tmp:$PYTHONPATH
python -v mcp_server/chroma_mcp_server_minimal.py [参数]
```

## 📈 集成场景

### 1. 实时查询系统
- **语义搜索**: 在已训练的向量数据库中进行实时搜索
- **相似度匹配**: 查找相关文档和内容
- **推荐系统**: 基于向量相似度的智能推荐

### 2. 艺术创作辅助
- **艺术家发现**: 智能艺术家推荐和组合
- **风格分析**: 深度艺术风格特征分析
- **创作指导**: 基于数据的创作建议

### 3. 研究和开发
- **数据探索**: 交互式向量空间探索
- **模型验证**: 验证向量化模型的效果
- **原型开发**: 快速构建基于向量的应用

## 🤝 与主项目的关系

这个 MCP 服务器是 Web2Embeddings AutoDL Package 的重要补充：

- **数据来源**: 使用主项目生成的 ChromaDB 向量数据库
- **模型一致**: 使用相同的 Jina Embeddings V3 模型
- **路径统一**: 遵循主项目的标准路径结构
- **功能互补**: 主项目负责训练，MCP 服务器负责查询

## 📞 技术支持

如遇问题，请：

1. 检查日志输出中的错误信息
2. 确认依赖包已正确安装
3. 验证数据库路径和集合名称
4. 查看主项目的故障排除指南
5. 在 GitHub Issues 中报告问题

---

**享受高效的向量查询体验！** 🎉