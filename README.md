# Web2Embeddings AutoDL Training Package 🚀

一个专为 AutoDL 平台设计的完整文本向量化训练包，使用 Jina Embeddings V3 模型进行高质量的文本嵌入生成。

## 🏗️ 项目特点

- ✅ **专为 AutoDL 优化**：完全适配 AutoDL 平台的运行环境
- ✅ **Jina Embeddings V3**：使用最新的 1024 维高质量嵌入模型
- ✅ **实时监控**：GPU/CPU/内存使用监控显示
- ✅ **智能批处理优化**：根据硬件自动调整批处理效率
- ✅ **可视化分析**：3D/2D 交互式嵌入空间可视化
- ✅ **ChromaDB 存储**：高性能向量数据库
- ✅ **Rich 库优化**：Rich 库提供的美观进度显示
- ✅ **MCP 服务器集成**：实时向量查询和艺术家分析功能

## 🗂️ 项目结构

```
web2embeddings_autodl_package/
├── config/
│   ├── autodl_config.json        # AutoDL 包配置
│   └── training_config.json      # 训练参数配置
├── data/
│   └── danbooru_training_data.jsonl # 训练数据（需要放置）
├── scripts/
│   ├── autodl_setup.sh           # 环境设置脚本
│   ├── run_vectorizer.sh         # 向量化运行脚本
│   └── run_visualizer.sh         # 可视化运行脚本
├── src/
│   ├── vectorizer.py             # 核心向量化逻辑
│   └── visualizer.py             # 可视化逻辑
├── mcp_server/                   # MCP 服务器目录
│   ├── chroma_mcp_server_minimal.py    # ChromaDB MCP 服务器
│   ├── start_mcp_server.sh             # MCP 服务器启动脚本
│   ├── test_mcp_server.py              # MCP 服务器测试工具
│   ├── config/                         # MCP 服务器配置
│   └── examples/                       # MCP 配置示例
├── main.py                       # 主程序入口
├── requirements.txt              # Python 依赖
└── README.md                     # 项目说明
```

## 🚀 AutoDL 快速开始

### 1. 准备数据
将您的训练数据以 JSONL 格式准备好，每行包含：
```json
{"id": "unique_id", "text": "要向量化的文本内容", "source": "数据来源路径"}
```

### 2. 上传到 AutoDL
1. 将项目打包为 `web2embeddings_autodl_package.zip`
2. 上传到 AutoDL，会自动解压到 `/root/autodl-tmp/` 目录
3. 将训练数据放置到 `/root/autodl-tmp/data/danbooru_training_data.jsonl`

### 3. 环境设置
```bash
cd /root/autodl-tmp
bash scripts/autodl_setup.sh
```

### 4. 运行向量化
```bash
bash scripts/run_vectorizer.sh
```

### 5. 生成可视化（可选）
```bash
bash scripts/run_visualizer.sh
```

### 6. 启动 MCP 服务器（新功能）
```bash
bash mcp_server/start_mcp_server.sh
```

## ⚙️ 配置说明

### training_config.json 参数

```json
{
  "input": "/root/autodl-tmp/data/danbooru_training_data.jsonl",  // 输入数据路径
  "db": "/root/autodl-tmp/artifacts/vector_stores/chroma_db",     // 数据库存储路径
  "model": "jinaai/jina-embeddings-v3",                          // 模型名称
  "task": "retrieval.passage",                                   // 任务类型
  "truncate_dim": null,                                          // 截断维度（null=1024维）
  "max_length": 8192,                                            // 最大序列长度
  "batch_size": 32,                                              // 批处理大小
  "device": "cuda"                                               // 运行设备
}
```

### 任务类型说明
- `retrieval.passage`：文档检索（推荐）
- `retrieval.query`：查询检索
- `classification`：文本分类
- `text-matching`：文本匹配
- `separation`：文本分离

## 🚨 MCP 服务器功能

### 🎯 核心功能
- **实时向量查询**：在已训练的向量数据库中进行语义搜索
- **艺术家分析工作流**：专门优化的艺术家推荐和组合功能
- **用户记忆系统**：保存和检索用户的分析偏好
- **FastMCP 集成**：现代化的 MCP 服务器框架

### 🛠️ MCP 服务器使用

#### 启动服务器
```bash
# 使用启动脚本（推荐）
bash mcp_server/start_mcp_server.sh

# 手动启动
python mcp_server/chroma_mcp_server_minimal.py \
    --chromadb-path /root/autodl-tmp/artifacts/vector_stores/chroma_db \
    --collection-name danbooru_training_data_jina-embeddings-v3 \
    --model-name jinaai/jina-embeddings-v3 \
    --device auto
```

#### Cursor IDE 集成
将以下配置添加到 Cursor 的 MCP 配置文件：
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

#### 功能测试
```bash
# 运行完整测试套件
python mcp_server/test_mcp_server.py

# 跳过特定测试
python mcp_server/test_mcp_server.py --skip-direct --skip-mcp
```

### 🎨 艺术家分析工作流
当查询包含艺术家名称时，MCP 服务器会自动：
1. **详细艺术家分析**：分析艺术家的核心创作主题和风格特征
2. **相似艺术家发现**：基于核心标签和风格特征智能推荐
3. **组合字符串生成**：生成可直接使用的艺术家组合格式
4. **详细解释说明**：每个推荐艺术家的特点和匹配原因

**输出示例格式**:
```
(artist:as109:1.1), ((artist:nudiedoodles, artist:ishikei)), (artist:legendarysoulii, artist:littleloli)
```

## 🗃️ 输出结构

### 向量数据库
- **位置**：`/root/autodl-tmp/artifacts/vector_stores/chroma_db/`
- **格式**：ChromaDB 数据库
- **内容**：文本嵌入向量 + 元数据

### 可视化文件
- **位置**：`/root/autodl-tmp/artifacts/visualizations/`
- **格式**：交互式 HTML 文件
- **功能**：3D/2D 嵌入空间可视化

### 日志信息
- **集群信息**：`artifacts/vector_stores/collections.txt`
- **处理统计**：实时显示在控制台

## 🔧 高级用法

### 自定义参数运行

```bash
python main.py --config custom_config.json
```

### 直接调用向量化器

```bash
python src/vectorizer.py \
    --input data/custom_data.jsonl \
    --model jinaai/jina-embeddings-v3 \
    --batch-size 64 \
    --device cuda
```

### 自定义可视化

```bash
python src/visualizer.py \
    --db artifacts/vector_stores/chroma_db \
    --collection your_collection_name \
    --max-points 5000 \
    --clusters 15
```

## 💡 性能优化建议

### GPU 设备
- **推荐配置**：RTX 3090/4090 或 V100/A100
- **最小显存**：8GB（batch_size=16）
- **推荐显存**：24GB（batch_size=64）

### 批处理大小调整
```python
# 根据 GPU 显存调整
"batch_size": 16,  # 8GB 显存
"batch_size": 32,  # 16GB 显存
"batch_size": 64,  # 24GB+ 显存
```

### 数据量建议
- **小数据集**：< 10K 文档
- **中等数据集**：10K - 100K 文档
- **大数据集**：100K+ 文档（建议分批处理）

### 基础性能指标（RTX 4090）
- **处理速度**：~540-1000 文档/秒
- **token 处理**：~45K-100K tokens/秒
- **内存占用**：~4-8GB GPU 显存

### 典型数据量处理时间
- **10K 文档**：~2-5 分钟
- **50K 文档**：~10-20 分钟
- **100K 文档**：~30-60 分钟

## 🎮 应用场景

1. **语义搜索**：构建智能文档检索系统
2. **RAG 系统**：为大模型提供知识库支持
3. **文本聚类**：自动文档分类和主题发现
4. **相似度匹配**：找到相似文档内容
5. **推荐系统**：基于内容的智能推荐
6. **艺术创作辅助**：智能艺术家推荐和组合（MCP 服务器）

## ⚡ 高级特性

### 自定义参数运行

```bash
python main.py --config custom_config.json
```

### 直接调用向量化器

```bash
python src/vectorizer.py \
    --input data/custom_data.jsonl \
    --model jinaai/jina-embeddings-v3 \
    --batch-size 64 \
    --device cuda
```

### 自定义可视化

```bash
python src/visualizer.py \
    --db artifacts/vector_stores/chroma_db \
    --collection your_collection_name \
    --max-points 5000 \
    --clusters 15
```

## 📊 性能优化

### GPU 设备
- **推荐配置**：RTX 3090/4090 或 V100/A100
- **最小显存**：8GB（batch_size=16）
- **推荐显存**：24GB（batch_size=64）

### 批处理大小调整
```python
# 根据 GPU 显存调整
"batch_size": 16,  # 8GB 显存
"batch_size": 32,  # 16GB 显存
"batch_size": 64,  # 24GB+ 显存
```

### 数据量建议
- **小数据集**：< 10K 文档
- **中等数据集**：10K - 100K 文档
- **大数据集**：100K+ 文档（建议分批处理）

## 💡 使用场景

1. **语义搜索**：构建智能文档检索系统
2. **RAG 系统**：为大模型提供知识库支持
3. **文本聚类**：自动文档分类和主题发现
4. **相似度匹配**：找到相似文档内容
5. **推荐系统**：基于内容的智能推荐

## ⚠️ 注意事项

### Q: CUDA 内存不足
**A**：减少 batch_size 或使用 CPU 模式
```json
{"batch_size": 16, "device": "cpu"}
```

### Q: 模型下载失败
**A**：检查网络连接或使用镜像端点
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q: ChromaDB 权限错误
**A**：确保输出目录有写入权限
```bash
chmod -R 755 /root/autodl-tmp/artifacts/
```

## 🔧 故障排除

### MCP 服务器问题

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

## 🤝 贡献

如有问题，请在 GitHub Issues 中提出。

## 📞 技术支持

如遇问题，请：

1. 检查日志输出中的错误信息
2. 确认依赖包已正确安装
3. 验证数据库路径和集合名称
4. 查看项目的故障排除指南
5. 在 GitHub Issues 中报告问题

---

**Happy Vectorizing! 🎉**