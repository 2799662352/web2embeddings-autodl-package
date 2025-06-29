#!/usr/bin/env python3
"""
示例数据生成器
用于生成测试用的 JSONL 数据文件
"""

import json
import random
import uuid
from datetime import datetime


def generate_sample_texts():
    """生成多样化的示例文本内容"""
    
    # 不同类型的示例文本
    tech_texts = [
        "人工智能技术正在快速发展，机器学习和深度学习已经成为推动科技进步的重要力量。",
        "云计算为企业提供了灵活、可扩展的IT基础设施解决方案，显著降低了运营成本。",
        "区块链技术具有去中心化、不可篡改的特点，在金融、供应链等领域有广泛应用前景。",
        "物联网连接了数十亿设备，为智慧城市和工业4.0的发展提供了技术基础。",
        "5G网络的部署将大幅提升数据传输速度，为远程医疗、自动驾驶等应用创造条件。"
    ]
    
    science_texts = [
        "量子计算利用量子力学原理进行信息处理，有望在特定问题上实现指数级的性能提升。",
        "基因编辑技术CRISPR为治疗遗传疾病和改良农作物品种提供了革命性的工具。",
        "可再生能源技术的快速发展正在改变全球能源格局，太阳能和风能成本持续下降。",
        "太空探索技术的进步使得火星殖民和小行星采矿等概念变得更加现实。",
        "纳米技术在材料科学、医学和电子产品等领域展现出巨大的应用潜力。"
    ]
    
    business_texts = [
        "数字化转型已成为企业保持竞争力的关键策略，涉及业务流程、客户体验等多个方面。",
        "电子商务平台的兴起改变了消费者的购物习惯，线上线下融合成为新的发展趋势。",
        "数据分析和商业智能工具帮助企业从海量数据中提取有价值的洞察和决策支持。",
        "可持续发展和ESG（环境、社会、治理）标准越来越受到投资者和消费者的关注。",
        "远程工作模式的普及改变了传统的办公文化，对企业管理提出了新的挑战。"
    ]
    
    culture_texts = [
        "传统文化与现代科技的融合创造了新的艺术表达形式和文化传播方式。",
        "全球化进程中的文化交流促进了不同文明之间的理解和包容。",
        "数字化时代的文化产业面临着机遇和挑战，内容创作和版权保护成为关键议题。",
        "教育技术的发展为个性化学习和终身教育提供了新的可能性。",
        "社交媒体平台改变了信息传播和社会互动的方式，对文化形成产生深远影响。"
    ]
    
    return tech_texts + science_texts + business_texts + culture_texts


def generate_sample_data(num_docs=1000, output_file="data/danbooru_training_data.jsonl"):
    """生成示例训练数据
    
    Args:
        num_docs: 要生成的文档数量
        output_file: 输出文件路径
    """
    
    sample_texts = generate_sample_texts()
    
    print(f"正在生成 {num_docs} 个示例文档...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in range(num_docs):
            # 随机选择基础文本
            base_text = random.choice(sample_texts)
            
            # 添加一些变化
            variations = [
                f"在当今快速发展的世界中，{base_text}",
                f"研究表明，{base_text}",
                f"专家认为，{base_text}",
                f"根据最新报告，{base_text}",
                f"随着技术的不断进步，{base_text}",
                base_text,  # 保持原文
                f"{base_text}这一趋势值得我们深入思考和关注。",
                f"{base_text}未来的发展前景令人期待。"
            ]
            
            final_text = random.choice(variations)
            
            # 生成文档记录
            doc = {
                "id": f"doc_{i:06d}",
                "text": final_text,
                "source": f"sample_data/category_{i % 4}/document_{i}.txt"
            }
            
            # 写入 JSONL 文件
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
    
    print(f"✅ 成功生成 {num_docs} 个示例文档，保存到: {output_file}")
    print(f"📊 文件大小: {get_file_size(output_file)}")
    
    # 显示前几行作为示例
    print("\n📋 前3行示例:")
    with open(output_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            data = json.loads(line)
            print(f"{i+1}. ID: {data['id']}, Text: {data['text'][:50]}...")


def get_file_size(file_path):
    """获取文件大小的人类可读格式"""
    import os
    size_bytes = os.path.getsize(file_path)
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"


def validate_jsonl(file_path):
    """验证 JSONL 文件格式"""
    print(f"\n🔍 验证文件格式: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            valid_lines = 0
            total_lines = 0
            
            for line_num, line in enumerate(f, 1):
                total_lines += 1
                line = line.strip()
                
                if not line:  # 跳过空行
                    continue
                    
                try:
                    data = json.loads(line)
                    
                    # 检查必需字段
                    if 'id' in data and 'text' in data and 'source' in data:
                        valid_lines += 1
                    else:
                        print(f"⚠️  第 {line_num} 行缺少必需字段: {data}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ 第 {line_num} 行 JSON 格式错误: {e}")
            
            print(f"✅ 验证完成: {valid_lines}/{total_lines} 行格式正确")
            return valid_lines == total_lines
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="生成示例训练数据")
    parser.add_argument("--num-docs", "-n", type=int, default=1000,
                        help="要生成的文档数量 (默认: 1000)")
    parser.add_argument("--output", "-o", type=str, default="data/danbooru_training_data.jsonl",
                        help="输出文件路径 (默认: data/danbooru_training_data.jsonl)")
    parser.add_argument("--validate", "-v", action="store_true",
                        help="生成后验证文件格式")
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # 生成示例数据
    generate_sample_data(args.num_docs, args.output)
    
    # 验证格式（如果请求）
    if args.validate:
        validate_jsonl(args.output)
    
    print("\n🎉 示例数据生成完成！")
    print(f"💡 使用方法: python main.py 或 bash scripts/run_vectorizer.sh")