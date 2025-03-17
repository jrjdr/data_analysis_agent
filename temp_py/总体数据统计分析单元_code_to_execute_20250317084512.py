import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime

def analyze_general_statistics(file_path):
    """
    对CSV文件进行总体数据统计和基本分析
    
    参数:
    file_path (str): CSV文件路径
    
    返回:
    dict: 包含数据分析结果的字典
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 基本信息
        basic_info = {
            "file_path": file_path,
            "row_count": len(df),
            "column_count": len(df.columns),
            "file_size_kb": round(os.path.getsize(file_path) / 1024, 2),
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 列信息分析
        columns_info = {}
        for column in df.columns:
            column_data = {
                "type": str(df[column].dtype),
                "missing_values": int(df[column].isna().sum()),
                "missing_percentage": round(df[column].isna().sum() / len(df) * 100, 2)
            }
            
            # 数值列的统计分析
            if np.issubdtype(df[column].dtype, np.number):
                column_data.update({
                    "unique_values": int(df[column].nunique()),
                    "min": float(df[column].min()),
                    "max": float(df[column].max()),
                    "mean": float(df[column].mean()),
                    "median": float(df[column].median()),
                    "std": float(df[column].std()),
                    "q1": float(df[column].quantile(0.25)),
                    "q3": float(df[column].quantile(0.75))
                })
            # 分类列的统计分析
            else:
                column_data.update({
                    "unique_values": int(df[column].nunique()),
                    "most_common": {
                        "value": str(df[column].value_counts().index[0]),
                        "count": int(df[column].value_counts().iloc[0])
                    },
                    "least_common": {
                        "value": str(df[column].value_counts().index[-1]),
                        "count": int(df[column].value_counts().iloc[-1])
                    },
                    "top_5_values": [{
                        "value": str(value),
                        "count": int(count),
                        "percentage": round(count / len(df) * 100, 2)
                    } for value, count in df[column].value_counts().head(5).items()]
                })
            
            columns_info[column] = column_data
        
        # 计算相关性矩阵（仅针对数值列）
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        correlation = {}
        if len(numeric_columns) > 1:
            corr_matrix = df[numeric_columns].corr().round(3).to_dict()
            correlation = {
                "matrix": corr_matrix,
                "strongest_positive": {"columns": None, "value": 0},
                "strongest_negative": {"columns": None, "value": 0}
            }
            
            # 找出最强的正相关和负相关
            for col1 in numeric_columns:
                for col2 in numeric_columns:
                    if col1 != col2:
                        corr_value = corr_matrix[col1][col2]
                        if corr_value > correlation["strongest_positive"]["value"]:
                            correlation["strongest_positive"]["columns"] = f"{col1} & {col2}"
                            correlation["strongest_positive"]["value"] = corr_value
                        if corr_value < correlation["strongest_negative"]["value"]:
                            correlation["strongest_negative"]["columns"] = f"{col1} & {col2}"
                            correlation["strongest_negative"]["value"] = corr_value
        
        # 汇总结果
        results = {
            "basic_info": basic_info,
            "columns_info": columns_info,
            "correlation": correlation
        }
        
        return results
    
    except Exception as e:
        return {"error": str(e)}

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("Usage: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
    
    # 进行数据分析
    results = analyze_general_statistics(file_path)
    
    # 保存结果到JSON文件
    output_file = "general_statistics_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Analysis completed. Results saved to {output_file}")

if __name__ == "__main__":
    main()