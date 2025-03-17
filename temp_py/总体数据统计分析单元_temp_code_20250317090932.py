import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime

def analyze_data(file_path):
    """
    对CSV文件进行基本数据分析
    
    参数:
        file_path: CSV文件路径
    
    返回:
        包含分析结果的字典
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 基本信息
        basic_info = {
            "file_path": file_path,
            "row_count": len(df),
            "column_count": len(df.columns),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 列信息分析
        columns_info = {}
        for column in df.columns:
            col_info = {
                "type": str(df[column].dtype)
            }
            
            # 缺失值统计
            missing_count = df[column].isna().sum()
            col_info["missing_values"] = int(missing_count)
            col_info["missing_percentage"] = round(float(missing_count / len(df) * 100), 2)
            
            # 唯一值统计
            unique_count = df[column].nunique()
            col_info["unique_values"] = int(unique_count)
            
            # 数值列统计
            if pd.api.types.is_numeric_dtype(df[column]):
                col_info["min"] = float(df[column].min())
                col_info["max"] = float(df[column].max())
                col_info["mean"] = float(df[column].mean())
                col_info["median"] = float(df[column].median())
                col_info["std"] = float(df[column].std())
                col_info["25th_percentile"] = float(df[column].quantile(0.25))
                col_info["75th_percentile"] = float(df[column].quantile(0.75))
            
            # 分类列统计
            if pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_categorical_dtype(df[column]):
                value_counts = df[column].value_counts()
                if not value_counts.empty:
                    most_common_value = value_counts.index[0]
                    most_common_count = int(value_counts.iloc[0])
                    col_info["most_common"] = {
                        "value": most_common_value,
                        "count": most_common_count,
                        "percentage": round(float(most_common_count / len(df) * 100), 2)
                    }
                    
                    # 获取前5个最常见值的分布
                    top_values = {}
                    for i, (val, count) in enumerate(value_counts.head(5).items()):
                        top_values[str(val)] = {
                            "count": int(count),
                            "percentage": round(float(count / len(df) * 100), 2)
                        }
                    col_info["top_values"] = top_values
            
            columns_info[column] = col_info
        
        # 汇总结果
        result = {
            "basic_info": basic_info,
            "columns": columns_info
        }
        
        # 添加相关性分析（仅针对数值列）
        numeric_columns = df.select_dtypes(include=['number']).columns
        if len(numeric_columns) > 1:
            correlation_matrix = df[numeric_columns].corr().round(3).to_dict()
            result["correlation"] = correlation_matrix
        
        return result
    
    except Exception as e:
        return {"error": str(e)}

def main():
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("用法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    
    # 分析数据
    results = analyze_data(file_path)
    
    # 保存结果到JSON文件
    output_file = 'general_statistics_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"分析完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    main()