#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime

def analyze_dataset(file_path):
    """
    对给定CSV文件进行基本数据分析
    """
    try:
        # 读取数据
        print(f"正在读取数据: {file_path}")
        df = pd.read_csv(file_path)
        
        # 基本信息统计
        basic_info = {
            "file_path": file_path,
            "row_count": len(df),
            "column_count": len(df.columns),
            "file_size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2),
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 列信息分析
        columns_info = {}
        
        for column in df.columns:
            col_data = df[column]
            col_type = str(col_data.dtype)
            
            # 基本列信息
            column_stats = {
                "type": col_type,
                "missing_values": int(col_data.isna().sum()),
                "missing_percentage": round(col_data.isna().sum() / len(df) * 100, 2)
            }
            
            # 根据数据类型进行不同的统计
            if col_type in ['int64', 'float64']:
                # 数值型列统计
                column_stats.update({
                    "unique_values": int(col_data.nunique()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "25th_percentile": float(col_data.quantile(0.25)),
                    "75th_percentile": float(col_data.quantile(0.75))
                })
            else:
                # 分类型列统计
                column_stats.update({
                    "unique_values": int(col_data.nunique()),
                    "most_common_values": col_data.value_counts().head(5).to_dict(),
                    "least_common_values": col_data.value_counts().tail(5).to_dict()
                })
            
            columns_info[column] = column_stats
        
        # 特殊分析：基站分布
        if 'base_station_id' in df.columns and 'base_station_name' in df.columns:
            base_station_stats = df.groupby(['base_station_id', 'base_station_name']).size().reset_index()
            base_station_stats.columns = ['base_station_id', 'base_station_name', 'count']
            base_station_distribution = base_station_stats.to_dict('records')
        else:
            base_station_distribution = None
        
        # 特殊分析：状态分布
        if 'status' in df.columns:
            status_distribution = df['status'].value_counts().to_dict()
        else:
            status_distribution = None
        
        # 特殊分析：信号类型分布
        if 'signal_type' in df.columns:
            signal_type_distribution = df['signal_type'].value_counts().to_dict()
        else:
            signal_type_distribution = None
        
        # 汇总结果
        results = {
            "basic_info": basic_info,
            "columns_info": columns_info,
            "special_analysis": {
                "base_station_distribution": base_station_distribution,
                "status_distribution": status_distribution,
                "signal_type_distribution": signal_type_distribution
            }
        }
        
        return results
    
    except Exception as e:
        return {"error": str(e)}

def main():
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    
    # 分析数据
    results = analyze_dataset(file_path)
    
    # 保存结果到JSON文件
    output_file = 'general_statistics_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"分析结果已保存到: {output_file}")

if __name__ == "__main__":
    main()