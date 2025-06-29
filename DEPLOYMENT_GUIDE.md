# Web2Embeddings AutoDL 部署指南 📋

本指南提供在 AutoDL 平台上部署和使用 Web2Embeddings 训练包的详细步骤。

## 📋 部署前准备

### 1. 环境要求检查

**必需环境**：
- AutoDL 实例（推荐 GPU 实例）
- Python 3.8+ 
- CUDA 11.8+（GPU 模式）
- 至少 16GB 系统内存
- 至少 20GB 可用存储空间

**推荐 GPU 配置**：
- RTX 3090/4090 (24GB VRAM)
- V100 (32GB VRAM) 
- A100 (40GB/80GB VRAM)

### 2. 数据准备

将您的文本数据准备为 JSONL 格式：

```bash
# 示例数据格式
{"id": "doc_001", "text": "要向量化的文本内容", "source": "source_file.txt"}
{"id": "doc_002", "text": "另一段文本内容", "source": "another_file.txt"}
```

**数据质量要求**：
- 每行一个有效的 JSON 对象
- 文本长度建议 100-8000 字符
- UTF-8 编码
- 建议至少 1000 个文档

## 🚀 部署步骤

### 步骤 1: 下载项目

```bash
# 在 AutoDL 实例中下载项目
cd /root/autodl-tmp
git clone https://github.com/2799662352/web2embeddings-autodl-package.git
cd web2embeddings-autodl-package
```

### 步骤 2: 放置训练数据

```bash
# 将您的 JSONL 数据文件放置到 data 目录
cp /path/to/your/data.jsonl data/danbooru_training_data.jsonl

# 验证数据格式
head -5 data/danbooru_training_data.jsonl
wc -l data/danbooru_training_data.jsonl
```

### 步骤 3: 环境设置

```bash
# 运行自动设置脚本
bash scripts/autodl_setup.sh

# 或者手动安装依赖
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 步骤 4: 配置调整（可选）

根据您的 GPU 内存调整批处理大小：

```bash
# 编辑配置文件
vim config/training_config.json
```

**内存配置建议**：
```json
{
  "batch_size": 16,  // 8GB VRAM
  "batch_size": 32,  // 16GB VRAM  
  "batch_size": 64,  // 24GB+ VRAM
  "device": "cuda"   // 或 "cpu" 如果没有 GPU
}
```

### 步骤 5: 运行向量化

```bash
# 使用脚本运行（推荐）
bash scripts/run_vectorizer.sh

# 或直接运行主程序
python main.py

# 自定义配置文件
python main.py --config custom_config.json
```

### 步骤 6: 生成可视化（可选）

```bash
# 生成3D/2D可视化
bash scripts/run_visualizer.sh

# 自定义可视化参数
python src/visualizer.py \
    --collection your_collection_name \
    --max-points 5000 \
    --clusters 15
```

## 📊 监控和调试

### 实时监控

程序运行时会显示：
- 实时 GPU/CPU/内存使用率
- 处理进度和剩余时间
- 每秒处理的文档/token数量
- 详细的性能统计

### 常见输出目录

```bash
# 向量数据库
/root/autodl-tmp/artifacts/vector_stores/chroma_db/

# 可视化文件  
/root/autodl-tmp/artifacts/visualizations/

# 日志文件
/root/autodl-tmp/artifacts/vector_stores/collections.txt
```

### 检查结果

```bash
# 检查生成的集合
cat artifacts/vector_stores/collections.txt

# 检查数据库大小
du -sh artifacts/vector_stores/chroma_db/

# 列出生成的可视化文件
ls -la artifacts/visualizations/
```

## 🔧 高级配置

### 自定义模型和参数

```bash
# 使用不同的模型
python src/vectorizer.py \
    --input data/custom_data.jsonl \
    --model sentence-transformers/all-MiniLM-L6-v2 \
    --task classification \
    --batch-size 64
```

### 性能调优

**GPU 内存优化**：
```json
{
  "batch_size": 16,        // 减少批大小
  "max_length": 4096,      // 减少最大长度
  "truncate_dim": 512      // 使用 Matryoshka 截断
}
```

**CPU 模式**：
```json
{
  "device": "cpu",
  "batch_size": 8         // CPU 模式下使用更小批大小
}
```

## 🐛 故障排除

### 常见错误及解决方案

#### 1. CUDA 内存不足
```bash
RuntimeError: CUDA out of memory
```
**解决方案**：
- 减少 `batch_size` 到 8 或 16
- 减少 `max_length` 到 4096
- 切换到 CPU 模式：`"device": "cpu"`

#### 2. 模型下载失败
```bash
HTTPError: 403 Client Error
```
**解决方案**：
```bash
# 设置 HuggingFace 镜像
export HF_ENDPOINT=https://hf-mirror.com
# 或者
export HF_HUB_OFFLINE=1  # 使用离线模式
```

#### 3. 权限错误
```bash
PermissionError: [Errno 13] Permission denied
```
**解决方案**：
```bash
# 修改权限
chmod -R 755 /root/autodl-tmp/artifacts/
mkdir -p /root/autodl-tmp/artifacts/vector_stores/
```

#### 4. JSON 解析错误
```bash
JSONDecodeError: Expecting value
```
**解决方案**：
```bash
# 验证 JSONL 格式
python -c "import json; [json.loads(line) for line in open('data/danbooru_training_data.jsonl') if line.strip()]"

# 清理数据文件
sed '/^$/d' data/danbooru_training_data.jsonl > data/cleaned_data.jsonl
```

## 📈 性能基准

### 处理速度参考（RTX 4090）

| 数据量 | batch_size | 处理时间 | 速度 |
|--------|------------|----------|------|
| 1K 文档 | 32 | ~30秒 | ~33 docs/sec |
| 10K 文档 | 32 | ~5分钟 | ~33 docs/sec |
| 50K 文档 | 64 | ~15分钟 | ~55 docs/sec |
| 100K 文档 | 64 | ~30分钟 | ~55 docs/sec |

### 内存使用参考

| batch_size | GPU 内存 | 系统内存 |
|------------|----------|----------|
| 16 | ~6GB | ~4GB |
| 32 | ~10GB | ~6GB |
| 64 | ~18GB | ~10GB |

## 🔄 数据更新和增量处理

### 增量数据处理

```bash
# 处理新数据时，系统会自动删除旧集合
# 如需保留历史数据，请备份数据库
cp -r artifacts/vector_stores/chroma_db artifacts/backup_$(date +%Y%m%d)

# 然后处理新数据
python main.py --config new_data_config.json
```

### 合并多个数据集

```bash
# 合并多个 JSONL 文件
cat data/dataset1.jsonl data/dataset2.jsonl > data/merged_dataset.jsonl

# 确保 ID 唯一性
python -c "
import json
seen = set()
with open('data/merged_dataset.jsonl', 'r') as f, open('data/unique_dataset.jsonl', 'w') as out:
    for line in f:
        data = json.loads(line)
        if data['id'] not in seen:
            seen.add(data['id'])
            out.write(line)
"
```

## 📝 最佳实践

### 1. 数据预处理
- 清理HTML标签和特殊字符
- 统一文本编码为UTF-8
- 移除过短（<50字符）或过长（>16K字符）的文档
- 确保每个文档有唯一的ID

### 2. 性能优化
- 根据GPU内存选择合适的batch_size
- 使用SSD存储以提高I/O性能
- 定期清理ChromaDB以释放空间

### 3. 监控和日志
- 保存处理日志以便问题排查
- 监控GPU温度和使用率
- 定期备份重要的向量数据库

### 4. 安全考虑
- 确保训练数据不包含敏感信息
- 注意模型许可证要求（Jina V3 仅限非商业使用）
- 定期更新依赖包以修复安全漏洞

---

## 🆘 获取帮助

如果遇到问题：

1. **检查日志**：查看控制台输出和错误信息
2. **验证环境**：确认 GPU、CUDA、Python 版本
3. **验证数据**：检查 JSONL 文件格式和编码
4. **查看文档**：参考 README.md 和本部署指南
5. **提交 Issue**：在 GitHub 仓库中报告问题

**联系方式**：
- GitHub Issues: https://github.com/2799662352/web2embeddings-autodl-package/issues
- 项目主页: https://github.com/2799662352/web2embeddings-autodl-package

---

**祝您使用愉快！🎉**