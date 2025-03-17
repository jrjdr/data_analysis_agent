import pandas as pd
import numpy as np
import json
import sys
from typing import Dict, Any

def analyze_csv(file_path: str) -> Dict[str, Any]:
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 基本信息
        result = {
            "file_path": file_path,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": {}
        }
        
        # 遍历每一列进行分析
        for col in df.columns:
            col_data = {
                "type": str(df[col].dtype),
                "missing_values": df[col].isnull().sum(),
                "unique_values": df[col].nunique()
            }
            
            # 数值列统计
            if pd.api.types.is_numeric_dtype(df[col]):
                col_data.update({
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std()
                })
            
            # 分类列统计
            elif pd.api.types.is_object_dtype(df[col]):
                value_counts = df[col].value_counts()
                col_data["most_common"] = {
                    "value": value_counts.index[0],
                    "count": int(value_counts.iloc[0])
                }
            
            result["columns"][col] = col_data
        
        return result
    
    except Exception as e:
        print(f"Error analyzing CSV: {str(e)}")
        return {}

def save_to_json(data: Dict[str, Any], output_file: str) -> None:
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results to JSON: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file_path>")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    output_file = 'general_statistics_results.json'
    
    analysis_results = analyze_csv(csv_file_path)
    if analysis_results:
        save_to_json(analysis_results, output_file)