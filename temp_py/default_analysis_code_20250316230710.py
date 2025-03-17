#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel数据分析脚本 - 自动生成的默认分析代码
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("错误: 请提供CSV文件路径作为命令行参数")
        print("用法: python script.py <csv_file_path>")
        return
    
    # 获取CSV文件路径
    csv_file = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"错误: 文件不存在: {csv_file}")
        return
    
    print(f"正在分析文件: {csv_file}")
    
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        
        # 创建输出文件
        output_file = 'analysis_results.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入标题
            f.write("=" * 80 + "\n")
            f.write(f"Excel数据分析报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"分析文件: {csv_file}\n")
            f.write("=" * 80 + "\n\n")
            
            # 基本信息
            f.write("1. 基本信息\n")
            f.write("-" * 80 + "\n")
            f.write(f"数据行数: {len(df)}\n")
            f.write(f"数据列数: {len(df.columns)}\n")
            f.write(f"列名: {', '.join(df.columns)}\n\n")
            
            # 缺失值分析
            f.write("2. 缺失值分析\n")
            f.write("-" * 80 + "\n")
            missing_values = df.isnull().sum()
            f.write("每列缺失值数量:\n")
            for col, missing in missing_values.items():
                if missing > 0:
                    f.write(f"- {col}: {missing} ({missing/len(df):.2%})\n")
            if missing_values.sum() == 0:
                f.write("数据中没有缺失值\n")
            f.write("\n")
            
            # 数据类型分析
            f.write("3. 数据类型分析\n")
            f.write("-" * 80 + "\n")
            f.write("列数据类型:\n")
            for col, dtype in df.dtypes.items():
                f.write(f"- {col}: {dtype}\n")
            f.write("\n")

            # 分类列分析
            f.write("5. 分类列分析\n")
            f.write("-" * 80 + "\n")

            f.write(f"5.1 Category 分析\n")
            f.write("-" * 40 + "\n")
            try:
                # 类别计数
                value_counts = df['Category'].value_counts()
                f.write(f"类别计数 (前10项):\n")
                for value, count in value_counts.head(10).items():
                    f.write(f"- {value}: {count} ({count/len(df):.2%})\n")
                f.write(f"唯一值数量: {df['Category'].nunique()}\n\n")
            except Exception as e:
                f.write(f"分析 Category 时出错: {str(e)}\n\n")

            f.write(f"5.1 Item 分析\n")
            f.write("-" * 40 + "\n")
            try:
                # 类别计数
                value_counts = df['Item'].value_counts()
                f.write(f"类别计数 (前10项):\n")
                for value, count in value_counts.head(10).items():
                    f.write(f"- {value}: {count} ({count/len(df):.2%})\n")
                f.write(f"唯一值数量: {df['Item'].nunique()}\n\n")
            except Exception as e:
                f.write(f"分析 Item 时出错: {str(e)}\n\n")

            f.write(f"5.1 Price 分析\n")
            f.write("-" * 40 + "\n")
            try:
                # 类别计数
                value_counts = df['Price'].value_counts()
                f.write(f"类别计数 (前10项):\n")
                for value, count in value_counts.head(10).items():
                    f.write(f"- {value}: {count} ({count/len(df):.2%})\n")
                f.write(f"唯一值数量: {df['Price'].nunique()}\n\n")
            except Exception as e:
                f.write(f"分析 Price 时出错: {str(e)}\n\n")

            f.write(f"5.1 Date 分析\n")
            f.write("-" * 40 + "\n")
            try:
                # 类别计数
                value_counts = df['Date'].value_counts()
                f.write(f"类别计数 (前10项):\n")
                for value, count in value_counts.head(10).items():
                    f.write(f"- {value}: {count} ({count/len(df):.2%})\n")
                f.write(f"唯一值数量: {df['Date'].nunique()}\n\n")
            except Exception as e:
                f.write(f"分析 Date 时出错: {str(e)}\n\n")

            f.write(f"5.1 Week 分析\n")
            f.write("-" * 40 + "\n")
            try:
                # 类别计数
                value_counts = df['Week'].value_counts()
                f.write(f"类别计数 (前10项):\n")
                for value, count in value_counts.head(10).items():
                    f.write(f"- {value}: {count} ({count/len(df):.2%})\n")
                f.write(f"唯一值数量: {df['Week'].nunique()}\n\n")
            except Exception as e:
                f.write(f"分析 Week 时出错: {str(e)}\n\n")

            f.write(f"5.1 Month 分析\n")
            f.write("-" * 40 + "\n")
            try:
                # 类别计数
                value_counts = df['Month'].value_counts()
                f.write(f"类别计数 (前10项):\n")
                for value, count in value_counts.head(10).items():
                    f.write(f"- {value}: {count} ({count/len(df):.2%})\n")
                f.write(f"唯一值数量: {df['Month'].nunique()}\n\n")
            except Exception as e:
                f.write(f"分析 Month 时出错: {str(e)}\n\n")

            f.write(f"5.1 Sales 分析\n")
            f.write("-" * 40 + "\n")
            try:
                # 类别计数
                value_counts = df['Sales'].value_counts()
                f.write(f"类别计数 (前10项):\n")
                for value, count in value_counts.head(10).items():
                    f.write(f"- {value}: {count} ({count/len(df):.2%})\n")
                f.write(f"唯一值数量: {df['Sales'].nunique()}\n\n")
            except Exception as e:
                f.write(f"分析 Sales 时出错: {str(e)}\n\n")

            f.write(f"5.1 Revenue 分析\n")
            f.write("-" * 40 + "\n")
            try:
                # 类别计数
                value_counts = df['Revenue'].value_counts()
                f.write(f"类别计数 (前10项):\n")
                for value, count in value_counts.head(10).items():
                    f.write(f"- {value}: {count} ({count/len(df):.2%})\n")
                f.write(f"唯一值数量: {df['Revenue'].nunique()}\n\n")
            except Exception as e:
                f.write(f"分析 Revenue 时出错: {str(e)}\n\n")

            # 结论
            f.write("8. 分析结论\n")
            f.write("-" * 80 + "\n")
            f.write("这是一个自动生成的数据分析报告，包含了基本的统计分析。\n")
            f.write("请根据以上分析结果，结合业务场景进行进一步解读。\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("分析完成\n")
        
        print(f"分析完成，结果已保存到: {output_file}")
    
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")

if __name__ == "__main__":
    main()
