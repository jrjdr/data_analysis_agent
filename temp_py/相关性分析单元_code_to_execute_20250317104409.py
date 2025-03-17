#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import json
import sys
import argparse
from typing import Dict, List, Tuple, Any

def analyze_correlations(csv_path: str, output_path: str = "correlations.json") -> None:
    """分析CSV文件中数值变量之间的相关性并保存结果为JSON格式"""
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        print(f"成功读取CSV文件: {csv_path}")
        
        # 区分数值型和分类型列
        categorical_cols = ['timestamp', 'base_station_id', 'base_station_name', 'signal_type', 'status']
        numeric_cols = [col for col in df.columns if col not in categorical_cols]
        
        if not numeric_cols:
            print("错误: 未找到数值型列")
            return
            
        print(f"找到的数值型列: {numeric_cols}")
        
        # 处理缺失值
        df_numeric = df[numeric_cols].copy()
        missing_before = df_numeric.isnull().sum().sum()
        if missing_before > 0:
            df_numeric.fillna(df_numeric.mean(), inplace=True)
            print(f"已处理 {missing_before} 个缺失值")
        
        # 计算相关系数
        corr_matrix = df_numeric.corr(method='pearson')
        
        # 找出相关系数绝对值大于0.5的变量对
        strong_correlations = []
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:
                    strong_correlations.append({
                        "variable1": numeric_cols[i],
                        "variable2": numeric_cols[j],
                        "correlation": float(corr_value)  # 确保JSON可序列化
                    })
        
        # 保存结果为JSON
        result = {
            "total_numeric_variables": len(numeric_cols),
            "strong_correlations": strong_correlations,
            "correlation_threshold": 0.5
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        print(f"分析完成! 发现 {len(strong_correlations)} 对强相关变量")
        print(f"结果已保存至: {output_path}")
        
    except FileNotFoundError:
        print(f"错误: 文件 '{csv_path}' 不存在")
    except pd.errors.EmptyDataError:
        print(f"错误: 文件 '{csv_path}' 为空或格式不正确")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="分析CSV数据文件中变量之间的相关性")
    parser.add_argument("csv_path", help="CSV文件路径")
    parser.add_argument("-o", "--output", default="correlations.json", help="输出JSON文件路径")
    args = parser.parse_args()
    
    analyze_correlations(args.csv_path, args.output)