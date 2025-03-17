import pandas as pd
import numpy as np
import json
import sys
from typing import Dict, Any

def analyze_data(file_path: str) -> Dict[str, Any]:
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 基本数据集信息
        basic_info = {
            "row_count": len(df),
            "column_count": len(df.columns)
        }
        
        # 列统计信息
        column_stats = {}
        for col in df.columns:
            col_type = str(df[col].dtype)
            missing_values = df[col].isnull().sum()
            unique_values = df[col].nunique()
            
            stats = {
                "type": col_type,
                "missing_values": int(missing_values),
                "unique_values": int(unique_values)
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                stats.update({
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std())
                })
            elif pd.api.types.is_object_dtype(df[col]):
                value_counts = df[col].value_counts()
                stats["most_common"] = {
                    "value": str(value_counts.index[0]),
                    "count": int(value_counts.iloc[0])
                }
            
            column_stats[col] = stats
        
        # 汇总结果
        results = {
            "file_path": file_path,
            "basic_info": basic_info,
            "column_stats": column_stats
        }
        
        return results
    
    except Exception as e:
        print(f"Error analyzing {str(e)}")
        return {}

def save_results(results: Dict[str, Any], output_file: str) -> None:
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file_path>")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    output_file = 'general_statistics_results.json'
    
    results = analyze_data(csv_file_path)
    if results:
        save_results(results, output_file)