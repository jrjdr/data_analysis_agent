import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime

def analyze_data(file_path):
    """
    对CSV文件进行基本数据分析
    """
    try:
        # 读取CSV文件
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        
        # 基本信息统计
        basic_info = {
            "file_path": file_path,
            "row_count": len(df),
            "column_count": len(df.columns),
            "file_size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2),
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 列信息统计
        columns_info = {}
        for column in df.columns:
            col_data = df[column]
            col_type = str(col_data.dtype)
            
            # 基本列信息
            column_stats = {
                "type": col_type,
                "missing_values": int(col_data.isna().sum()),
                "unique_values": int(col_data.nunique())
            }
            
            # 根据数据类型进行不同的统计
            if np.issubdtype(col_data.dtype, np.number):
                # 数值型数据统计
                column_stats.update({
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "25th_percentile": float(col_data.quantile(0.25)),
                    "75th_percentile": float(col_data.quantile(0.75))
                })
            else:
                # 分类型数据统计
                if col_data.nunique() <= 50:  # 只对唯一值较少的列进行分布统计
                    value_counts = col_data.value_counts().head(10).to_dict()
                    column_stats["value_distribution"] = {str(k): int(v) for k, v in value_counts.items()}
                
                # 最常见的值
                most_common = col_data.value_counts().iloc[0]
                most_common_value = col_data.value_counts().index[0]
                column_stats["most_common"] = {
                    "value": str(most_common_value),
                    "count": int(most_common)
                }
            
            columns_info[column] = column_stats
        
        # 计算相关性矩阵（仅针对数值列）
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) > 1:
            correlation_matrix = df[numeric_columns].corr().round(3).to_dict()
            # 找出高相关性的列对（相关系数绝对值 > 0.7）
            high_correlations = []
            for col1 in numeric_columns:
                for col2 in numeric_columns:
                    if col1 != col2 and abs(df[col1].corr(df[col2])) > 0.7:
                        high_correlations.append({
                            "column1": col1,
                            "column2": col2,
                            "correlation": round(float(df[col1].corr(df[col2])), 3)
                        })
        else:
            correlation_matrix = {}
            high_correlations = []
        
        # 汇总所有统计结果
        analysis_results = {
            "basic_info": basic_info,
            "columns": columns_info,
            "correlation_matrix": correlation_matrix,
            "high_correlations": high_correlations
        }
        
        # 保存结果到JSON文件
        output_file = "general_statistics_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"分析完成，结果已保存至 {output_file}")
        return analysis_results
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    
    analyze_data(file_path)