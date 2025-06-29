# 数据目录说明

## 数据格式要求

请将您的训练数据以 JSONL 格式放置在此目录下，文件名为 `danbooru_training_data.jsonl`。

### JSONL 格式示例

每行应包含一个 JSON 对象，包含以下字段：

```json
{"id": "doc_001", "text": "这是要向量化的文本内容", "source": "data/source_file.txt"}
{"id": "doc_002", "text": "另一段文本内容，可以是任意长度", "source": "data/another_file.txt"}
{"id": "doc_003", "text": "支持多语言文本，包括中文、英文等", "source": "data/multilingual.txt"}
```

### 字段说明

- **id** (必需): 文档的唯一标识符
- **text** (必需): 要进行向量化的文本内容
- **source** (必需): 文档的来源路径或标识

### 数据准备建议

1. **文本长度**: 建议每个文档的文本长度在 100-8000 字符之间
2. **文档数量**: 建议至少 1000 个文档以获得良好的向量化效果
3. **内容质量**: 确保文本内容清晰、完整，避免过多的格式符号
4. **编码格式**: 使用 UTF-8 编码

### 验证数据格式

```bash
# 检查文件格式
head -5 danbooru_training_data.jsonl

# 统计文档数量
wc -l danbooru_training_data.jsonl

# 验证 JSON 格式
python -c "import json; [json.loads(line) for line in open('danbooru_training_data.jsonl')]"
```

## 示例数据生成

如果您需要测试，可以使用以下 Python 脚本生成示例数据：

```python
import json

# 生成示例数据
sample_data = [
    {"id": f"doc_{i:04d}", "text": f"这是第{i}个示例文档的内容。", "source": f"sample_{i}.txt"}
    for i in range(1, 101)  # 生成100个示例文档
]

# 保存为 JSONL 文件
with open('danbooru_training_data.jsonl', 'w', encoding='utf-8') as f:
    for item in sample_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
```
