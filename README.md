# Web2Embeddings AutoDL Training Package 🚀

一个专为 AutoDL 平台设计的完整文本向量化训练包，使用 Jina Embeddings V3 模型进行高质量的文本嵌入生成。

## 📋 项目特性

- ✅ **专为 AutoDL 优化**：完全适配 AutoDL 平台的运行环境
- ✅ **Jina Embeddings V3**：使用最新的 1024 维高质量嵌入模型
- ✅ **实时监控**：GPU/CPU/内存使用率实时显示
- ✅ **批处理优化**：智能批处理提升处理效率
- ✅ **可视化分析**：3D/2D 交互式嵌入空间可视化
- ✅ **ChromaDB 存储**：高性能向量数据库存储
- ✅ **进度跟踪**：Rich 库提供的美观进度显示

## 📁 项目结构

```
web2embeddings_autodl_package/
├── config/
│   ├── autodl_config.json      # AutoDL 包配置
│   └── training_config.json    # 训练参数配置
├── data/
│   └── danbooru_training_data.jsonl # 训练数据（需要放置）
├── scripts/
│   ├── autodl_setup.sh         # 环境设置脚本
│   ├── run_vectorizer.sh       # 向量化运行脚本
│   └── run_visualizer.sh       # 可视化运行脚本
├── src/
│   ├── vectorizer.py           # 核心向量化逻辑
│   └── visualizer.py           # 可视化逻辑
├── main.py                     # 主程序入口
├── requirements.txt            # Python 依赖
└── README.md                   # 项目说明
```

## 🚀 AutoDL 快速开始

### 1. 准备数据
将您的训练数据以 JSONL 格式准备好，每行应包含：
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

## ⚙️ 配置说明

### training_config.json 参数

```json
{
  "input": "/root/autodl-tmp/data/danbooru_training_data.jsonl",  // 输入数据路径
  "db": "/root/autodl-tmp/artifacts/vector_stores/chroma_db",     // 数据库存储路径
  "model": "jinaai/jina-embeddings-v3",                          // 模型名称
  "task": "retrieval.passage",                                   // 任务类型
  "truncate_dim": null,                                           // 截断维度（null=1024维）
  "max_length": 8192,                                             // 最大序列长度
  "batch_size": 32,                                               // 批处理大小
  "device": "cuda"                                               // 运行设备
}
```

### 任务类型说明
- `retrieval.passage`：文档检索（推荐）
- `retrieval.query`：查询检索
- `classification`：文本分类
- `text-matching`：文本匹配
- `separation`：文本分离

## 📊 输出结果

### 向量数据库
- **位置**：`/root/autodl-tmp/artifacts/vector_stores/chroma_db/`
- **格式**：ChromaDB 数据库
- **内容**：文本嵌入向量 + 元数据

### 可视化文件
- **位置**：`/root/autodl-tmp/artifacts/visualizations/`
- **格式**：交互式 HTML 文件
- **功能**：3D/2D 嵌入空间可视化

### 日志记录
- **集合信息**：`artifacts/vector_stores/collections.txt`
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

### GPU 设置
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

## 🎯 应用场景

1. **语义搜索**：构建智能文档检索系统
2. **RAG 系统**：为大模型提供知识库支持
3. **文本聚类**：自动文档分类和主题发现
4. **相似度匹配**：找到相似文本内容
5. **推荐系统**：基于内容的智能推荐

## 📈 处理能力

### 基准性能（RTX 4090）
- **处理速度**：~500-1000 文档/秒
- **token 处理**：~50K-100K tokens/秒
- **内存占用**：~4-8GB GPU 显存

### 典型数据集处理时间
- **10K 文档**：~2-5 分钟
- **50K 文档**：~10-20 分钟
- **100K 文档**：~30-60 分钟

## ⚠️ 注意事项

### 许可证
- Jina Embeddings V3 使用 **CC BY-NC 4.0** 许可证
- **免费用于研究和非商业用途**
- **商业用途需要联系 Jina AI 获取许可**

### 环境要求
- **Python**：3.8+
- **CUDA**：11.8+（GPU 模式）
- **内存**：16GB+ 系统内存
- **存储**：根据数据集大小预留空间

### 数据格式
确保输入数据为有效的 JSONL 格式：
```bash
# 验证数据格式
head -5 data/danbooru_training_data.jsonl
```

## 🐛 常见问题

### Q: CUDA 内存不足
**A**: 减少 batch_size 或使用 CPU 模式
```json
{"batch_size": 16, "device": "cpu"}
```

### Q: 模型下载失败
**A**: 检查网络连接或使用镜像源
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q: ChromaDB 权限错误
**A**: 确保输出目录有写权限
```bash
chmod -R 755 /root/autodl-tmp/artifacts/
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请在 GitHub Issues 中提出。

---

**Happy Vectorizing! 🎉**