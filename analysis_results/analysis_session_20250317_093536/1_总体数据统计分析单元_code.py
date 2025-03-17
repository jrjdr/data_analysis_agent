import pandas as pd
import numpy as np
import json
import sys
import os
from typing import Dict, Any

def analyze_dataset(file_path: str) -> Dict[str, Any]:
    """
    对CSV数据集进行基本统计分析
    
    Args:
        file_path: CSV文件路径
        
    Returns:
        包含统计分析结果的字典
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 基本数据集信息
        basic_info = {
            "文件路径": file_path,
            "行数": len(df),
            "列数": len(df.columns),
            "内存使用(MB)": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
        
        # 列信息分析
        columns_info = {}
        for column in df.columns:
            col_data = df[column]
            col_type = str(col_data.dtype)
            
            # 基本列信息
            col_info = {
                "数据类型": col_type,
                "缺失值数量": int(col_data.isna().sum()),
                "缺失值百分比": round(col_data.isna().mean() * 100, 2)
            }
            
            # 根据数据类型进行不同的统计
            if col_type in ['int64', 'float64']:
                # 数值型数据统计
                col_info.update({
                    "唯一值数量": int(col_data.nunique()),
                    "最小值": float(col_data.min()),
                    "最大值": float(col_data.max()),
                    "均值": float(col_data.mean()),
                    "中位数": float(col_data.median()),
                    "标准差": float(col_data.std()),
                    "25%分位数": float(col_data.quantile(0.25)),
                    "75%分位数": float(col_data.quantile(0.75))
                })
            else:
                # 分类型数据统计
                col_info.update({
                    "唯一值数量": int(col_data.nunique()),
                    "最常见值": str(col_data.value_counts().index[0]),
                    "最常见值出现次数": int(col_data.value_counts().iloc[0]),
                    "最常见值占比": round(col_data.value_counts().iloc[0] / len(col_data) * 100, 2)
                })
                
                # 如果唯一值数量较少，添加值分布信息
                if col_data.nunique() <= 15:
                    distribution = col_data.value_counts().to_dict()
                    # 将键转换为字符串以确保JSON兼容性
                    distribution = {str(k): int(v) for k, v in distribution.items()}
                    col_info["值分布"] = distribution
            
            columns_info[column] = col_info
        
        # 相关性分析（仅针对数值列）
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        if len(numeric_columns) > 1:
            correlation_matrix = df[numeric_columns].corr().round(3).to_dict()
            # 将NaN值转换为None以确保JSON兼容性
            correlation_matrix = {k: {str(k2): (None if pd.isna(v2) else float(v2)) 
                                     for k2, v2 in v.items()} 
                                 for k, v in correlation_matrix.items()}
        else:
            correlation_matrix = {}
        
        # 汇总结果
        results = {
            "基本信息": basic_info,
            "列统计信息": columns_info,
            "数值列相关性": correlation_matrix
        }
        
        return results
    
    except Exception as e:
        return {"错误": f"分析过程中出现错误: {str(e)}"}

def main():
    """主函数，处理命令行参数并执行分析"""
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    
    # 执行分析
    results = analyze_dataset(file_path)
    
    # 保存结果到JSON文件
    output_file = 'general_statistics_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"分析完成，结果已保存至 {output_file}")

if __name__ == "__main__":
    main()