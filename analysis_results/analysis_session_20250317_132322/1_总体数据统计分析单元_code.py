import pandas as pd
import numpy as np
import json
from typing import Any

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def analyze_csv(file_path: str) -> dict:
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 基本描述性统计
        basic_stats = df.describe().to_dict()
        
        # 分析数值列和分类列
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        categorical_columns = df.select_dtypes(exclude=[np.number]).columns
        
        numeric_analysis = {}
        for col in numeric_columns:
            numeric_analysis[col] = {
                "mean": df[col].mean(),
                "median": df[col].median(),
                "std": df[col].std(),
                "min": df[col].min(),
                "max": df[col].max(),
                "missing_values": df[col].isnull().sum()
            }
        
        categorical_analysis = {}
        for col in categorical_columns:
            value_counts = df[col].value_counts()
            categorical_analysis[col] = {
                "unique_values": df[col].nunique(),
                "most_common": {
                    "value": value_counts.index[0],
                    "count": value_counts.iloc[0]
                },
                "missing_values": df[col].isnull().sum()
            }
        
        # 构建结果字典
        results = {
            "file_path": file_path,
            "row_count": len(df),
            "column_count": len(df.columns),
            "basic_stats": basic_stats,
            "numeric_analysis": numeric_analysis,
            "categorical_analysis": categorical_analysis
        }
        
        return results
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {}

def save_json(data: dict, output_path: str) -> None:
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        print(f"Analysis results saved to {output_path}")
    except Exception as e:
        print(f"Error saving JSON: {str(e)}")

if __name__ == "__main__":
    csv_path = "temp_csv/excel_data_20250317132321.csv"
    output_path = "pngs/analysis_results.json"
    
    analysis_results = analyze_csv(csv_path)
    if analysis_results:
        save_json(analysis_results, output_path)