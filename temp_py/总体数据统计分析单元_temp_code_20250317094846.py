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
        row_count = len(df)
        column_count = len(df.columns)
        print(f"数据集包含 {row_count} 行和 {column_count} 列")
        
        # 初始化结果字典
        results = {
            "file_path": file_path,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "row_count": row_count,
            "column_count": column_count,
            "columns": {}
        }
        
        # 遍历每一列进行分析
        for column in df.columns:
            print(f"正在分析列: {column}")
            column_data = {}
            
            # 数据类型
            column_data["type"] = str(df[column].dtype)
            
            # 缺失值统计
            missing_values = df[column].isna().sum()
            column_data["missing_values"] = int(missing_values)
            column_data["missing_percentage"] = float(missing_values / row_count * 100)
            
            # 唯一值计数
            unique_values = df[column].nunique()
            column_data["unique_values"] = int(unique_values)
            
            # 根据数据类型进行不同的统计
            if pd.api.types.is_numeric_dtype(df[column]):
                # 数值型数据统计
                column_data["min"] = float(df[column].min())
                column_data["max"] = float(df[column].max())
                column_data["mean"] = float(df[column].mean())
                column_data["median"] = float(df[column].median())
                column_data["std"] = float(df[column].std())
                column_data["25th_percentile"] = float(df[column].quantile(0.25))
                column_data["75th_percentile"] = float(df[column].quantile(0.75))
            else:
                # 分类型数据统计
                value_counts = df[column].value_counts()
                if len(value_counts) > 0:
                    most_common_value = value_counts.index[0]
                    most_common_count = int(value_counts.iloc[0])
                    column_data["most_common"] = {
                        "value": most_common_value,
                        "count": most_common_count,
                        "percentage": float(most_common_count / row_count * 100)
                    }
                    
                    # 如果唯一值不太多，则记录所有值的分布
                    if unique_values <= 20:
                        distribution = {}
                        for val, count in value_counts.items():
                            distribution[str(val)] = {
                                "count": int(count),
                                "percentage": float(count / row_count * 100)
                            }
                        column_data["distribution"] = distribution
            
            # 将列的分析结果添加到总结果中
            results["columns"][column] = column_data
        
        # 计算相关性矩阵（仅针对数值列）
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) >= 2:
            correlation_matrix = df[numeric_columns].corr().round(3).to_dict()
            results["correlation_matrix"] = correlation_matrix
        
        return results
    
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return {"error": str(e)}

def save_results(results, output_file="general_statistics_results.json"):
    """
    将分析结果保存为JSON文件
    """
    try:
        # 将NumPy类型转换为Python原生类型
        def convert_numpy_types(obj):
            if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(i) for i in obj]
            else:
                return obj
        
        results = convert_numpy_types(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到: {output_file}")
    except Exception as e:
        print(f"保存结果时出现错误: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python script.py <csv文件路径> [输出JSON文件路径]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "general_statistics_results.json"
    
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    
    results = analyze_data(file_path)
    save_results(results, output_file)