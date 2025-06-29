# 工具目录说明

本目录包含用于管理和维护 Web2Embeddings 项目的实用工具。

## 🛠️ 可用工具

### 1. data_validator.py - 数据验证工具

用于验证 JSONL 训练数据的格式和质量。

**使用方法:**
```bash
# 验证数据文件
python tools/data_validator.py data/danbooru_training_data.jsonl

# 保存验证报告
python tools/data_validator.py data/danbooru_training_data.jsonl --output validation_report.json
```

**功能:**
- ✅ JSON 格式验证
- ✅ 必需字段检查 (id, text, source)
- ✅ 重复 ID 检测
- ✅ 文本长度统计
- ✅ 数据模式分析
- ✅ 详细错误和警告报告

### 2. collection_manager.py - 集合管理工具

用于管理 ChromaDB 向量数据库集合。

**使用方法:**
```bash
# 列出所有集合
python tools/collection_manager.py list

# 检查特定集合
python tools/collection_manager.py inspect collection_name

# 在集合中搜索
python tools/collection_manager.py search collection_name "搜索内容"

# 导出集合数据
python tools/collection_manager.py export collection_name output.json

# 删除集合
python tools/collection_manager.py delete collection_name
```

**功能:**
- 📊 集合信息查看
- 🔍 语义搜索测试
- 📤 数据导出
- 🗑️ 集合删除
- 📈 统计分析

## 🚀 快速开始

### 验证您的数据

在开始训练之前，先验证数据格式：

```bash
python tools/data_validator.py data/danbooru_training_data.jsonl
```

如果验证通过，您将看到：
```
✅ 数据验证通过！
💡 建议:
  - 数据质量良好，可以开始向量化训练
```

### 训练完成后检查结果

训练完成后，检查生成的集合：

```bash
# 查看所有集合
python tools/collection_manager.py list

# 检查特定集合
python tools/collection_manager.py inspect danbooru_training_data_jina-embeddings-v3

# 测试搜索功能
python tools/collection_manager.py search danbooru_training_data_jina-embeddings-v3 "人工智能"
```

## 📋 常见使用场景

### 1. 数据准备阶段

```bash
# 1. 验证原始数据
python tools/data_validator.py raw_data.jsonl

# 2. 如果有错误，修复后重新验证
python tools/data_validator.py fixed_data.jsonl --output report.json

# 3. 将验证通过的数据移动到训练目录
cp fixed_data.jsonl data/danbooru_training_data.jsonl
```

### 2. 训练监控

```bash
# 训练过程中检查集合状态
watch -n 30 'python tools/collection_manager.py list'

# 训练完成后详细检查
python tools/collection_manager.py inspect your_collection_name
```

### 3. 结果验证

```bash
# 测试搜索功能
python tools/collection_manager.py search your_collection_name "测试查询" --limit 10

# 导出样本数据进行分析
python tools/collection_manager.py export your_collection_name sample.json --limit 100
```

### 4. 数据维护

```bash
# 备份重要集合
python tools/collection_manager.py export important_collection backup_$(date +%Y%m%d).json

# 清理不需要的集合
python tools/collection_manager.py delete old_collection --force
```

## ⚠️ 注意事项

### 数据验证工具
- 建议在每次训练前都运行数据验证
- 严重错误会导致训练失败，必须修复
- 警告不会阻止训练，但可能影响质量

### 集合管理工具
- 删除集合操作不可逆，请谨慎使用
- 导出大集合时可能需要较长时间
- 搜索功能需要相应的模型支持

## 🔧 自定义和扩展

这些工具都是开源的，您可以根据需要进行修改和扩展：

1. **添加新的验证规则**: 修改 `DataValidator` 类
2. **支持新的数据格式**: 扩展数据解析逻辑
3. **增加新的管理功能**: 扩展 `CollectionManager` 类
4. **集成到 CI/CD**: 将验证工具集成到自动化流程中

## 🐛 故障排除

### 常见问题

1. **权限错误**
   ```bash
   chmod +x tools/*.py
   ```

2. **模块导入错误**
   ```bash
   pip install -r requirements.txt
   ```

3. **数据库连接失败**
   ```bash
   # 检查数据库路径是否正确
   ls -la artifacts/vector_stores/chroma_db/
   ```

## 📞 获取帮助

如果遇到问题：

1. 查看工具的帮助信息：
   ```bash
   python tools/data_validator.py --help
   python tools/collection_manager.py --help
   ```

2. 在 GitHub Issues 中报告问题

3. 参考主项目的 README 和部署指南

---

**祝您使用愉快！🎉**
