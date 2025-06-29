#!/usr/bin/env python3
"""
数据验证工具
用于验证 JSONL 训练数据的格式和质量
"""

import json
import argparse
import os
from typing import Dict, List, Any
from collections import Counter
import re


class DataValidator:
    """JSONL 数据验证器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_lines': 0,
            'valid_docs': 0,
            'empty_lines': 0,
            'json_errors': 0,
            'missing_fields': 0,
            'duplicate_ids': 0,
            'text_lengths': [],
            'id_patterns': Counter(),
            'source_patterns': Counter()
        }
    
    def validate(self) -> Dict[str, Any]:
        """执行完整的数据验证"""
        print(f"🔍 验证数据文件: {self.file_path}")
        print("=" * 50)
        
        # 检查文件是否存在
        if not os.path.exists(self.file_path):
            self.errors.append(f"文件不存在: {self.file_path}")
            return self._generate_report()
        
        # 验证每行数据
        seen_ids = set()
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                self.stats['total_lines'] += 1
                
                # 跳过空行
                if not line.strip():
                    self.stats['empty_lines'] += 1
                    continue
                
                # 验证JSON格式
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    self.stats['json_errors'] += 1
                    self.errors.append(f"第 {line_num} 行 JSON 解析错误: {e}")
                    continue
                
                # 验证数据结构
                validation_result = self._validate_document(data, line_num)
                if validation_result['valid']:
                    self.stats['valid_docs'] += 1
                    
                    # 检查ID重复
                    doc_id = data['id']
                    if doc_id in seen_ids:
                        self.stats['duplicate_ids'] += 1
                        self.errors.append(f"第 {line_num} 行重复的ID: {doc_id}")
                    else:
                        seen_ids.add(doc_id)
                    
                    # 收集统计信息
                    self._collect_stats(data)
                else:
                    self.stats['missing_fields'] += 1
        
        # 生成报告
        return self._generate_report()
    
    def _validate_document(self, data: Dict, line_num: int) -> Dict[str, Any]:
        """验证单个文档的格式"""
        required_fields = ['id', 'text', 'source']
        missing_fields = []
        
        # 检查必需字段
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif not isinstance(data[field], str):
                self.warnings.append(f"第 {line_num} 行 '{field}' 字段应为字符串类型")
            elif not data[field].strip():
                self.warnings.append(f"第 {line_num} 行 '{field}' 字段为空")
        
        if missing_fields:
            self.errors.append(f"第 {line_num} 行缺少字段: {', '.join(missing_fields)}")
            return {'valid': False, 'missing_fields': missing_fields}
        
        # 检查文本长度
        text_length = len(data['text'])
        if text_length < 10:
            self.warnings.append(f"第 {line_num} 行文本过短 ({text_length} 字符)")
        elif text_length > 16384:
            self.warnings.append(f"第 {line_num} 行文本过长 ({text_length} 字符)")
        
        # 检查ID格式
        if not re.match(r'^[a-zA-Z0-9_-]+$', data['id']):
            self.warnings.append(f"第 {line_num} 行ID包含特殊字符: {data['id']}")
        
        return {'valid': True}
    
    def _collect_stats(self, data: Dict):
        """收集数据统计信息"""
        # 文本长度统计
        self.stats['text_lengths'].append(len(data['text']))
        
        # ID模式统计
        id_pattern = self._extract_pattern(data['id'])
        self.stats['id_patterns'][id_pattern] += 1
        
        # Source模式统计
        source_pattern = self._extract_pattern(data['source'])
        self.stats['source_patterns'][source_pattern] += 1
    
    def _extract_pattern(self, text: str) -> str:
        """提取字符串模式"""
        # 将数字替换为N，字母替换为A
        pattern = re.sub(r'\d+', 'N', text)
        pattern = re.sub(r'[a-zA-Z]+', 'A', pattern)
        return pattern
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        report = {
            'file_path': self.file_path,
            'validation_passed': len(self.errors) == 0,
            'stats': self.stats.copy(),
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy()
        }
        
        # 计算文本长度统计
        if self.stats['text_lengths']:
            lengths = self.stats['text_lengths']
            report['stats']['text_length_stats'] = {
                'min': min(lengths),
                'max': max(lengths),
                'avg': sum(lengths) / len(lengths),
                'median': sorted(lengths)[len(lengths) // 2]
            }
        
        # 打印报告
        self._print_report(report)
        
        return report
    
    def _print_report(self, report: Dict):
        """打印验证报告"""
        stats = report['stats']
        
        print("\n📊 数据统计:")
        print(f"  总行数: {stats['total_lines']}")
        print(f"  有效文档: {stats['valid_docs']}")
        print(f"  空行: {stats['empty_lines']}")
        print(f"  JSON错误: {stats['json_errors']}")
        print(f"  缺少字段: {stats['missing_fields']}")
        print(f"  重复ID: {stats['duplicate_ids']}")
        
        if 'text_length_stats' in stats:
            length_stats = stats['text_length_stats']
            print(f"\n📏 文本长度统计:")
            print(f"  最短: {length_stats['min']} 字符")
            print(f"  最长: {length_stats['max']} 字符")
            print(f"  平均: {length_stats['avg']:.0f} 字符")
            print(f"  中位数: {length_stats['median']} 字符")
        
        # 显示常见模式
        if stats['id_patterns']:
            print(f"\n🔍 ID模式 (前5个):")
            for pattern, count in stats['id_patterns'].most_common(5):
                print(f"  {pattern}: {count} 次")
        
        if stats['source_patterns']:
            print(f"\n📁 Source模式 (前5个):")
            for pattern, count in stats['source_patterns'].most_common(5):
                print(f"  {pattern}: {count} 次")
        
        # 显示错误
        if report['errors']:
            print(f"\n❌ 错误 ({len(report['errors'])} 个):")
            for error in report['errors'][:10]:  # 只显示前10个错误
                print(f"  {error}")
            if len(report['errors']) > 10:
                print(f"  ... 还有 {len(report['errors']) - 10} 个错误")
        
        # 显示警告
        if report['warnings']:
            print(f"\n⚠️  警告 ({len(report['warnings'])} 个):")
            for warning in report['warnings'][:10]:  # 只显示前10个警告
                print(f"  {warning}")
            if len(report['warnings']) > 10:
                print(f"  ... 还有 {len(report['warnings']) - 10} 个警告")
        
        # 验证结果
        print(f"\n{'=' * 50}")
        if report['validation_passed']:
            print("✅ 数据验证通过！")
        else:
            print("❌ 数据验证失败，请修复上述错误后重试。")
        
        # 建议
        print(f"\n💡 建议:")
        if stats['valid_docs'] < 1000:
            print("  - 建议至少有 1000 个有效文档以获得更好的向量化效果")
        if 'text_length_stats' in stats:
            avg_length = stats['text_length_stats']['avg']
            if avg_length < 100:
                print("  - 文档平均长度较短，可能影响向量化质量")
            elif avg_length > 8000:
                print("  - 文档平均长度较长，建议考虑分段处理")


def main():
    parser = argparse.ArgumentParser(description="验证 JSONL 训练数据格式")
    parser.add_argument("file_path", help="JSONL 数据文件路径")
    parser.add_argument("--output", "-o", help="将验证报告保存到 JSON 文件")
    
    args = parser.parse_args()
    
    # 执行验证
    validator = DataValidator(args.file_path)
    report = validator.validate()
    
    # 保存报告（如果指定）
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 验证报告已保存到: {args.output}")
    
    # 返回适当的退出码
    exit(0 if report['validation_passed'] else 1)


if __name__ == "__main__":
    main()