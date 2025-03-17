import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats import f_oneway
import json
import sys
import os
from typing import Dict, List, Any, Tuple

def load_data(file_path: str) -> pd.DataFrame:
    """加载CSV数据文件"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"加载数据文件时出错: {e}")
        sys.exit(1)

def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """获取数据框中的数值型列"""
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()

def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """获取数据框中的分类列"""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def calculate_correlations(df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
    """计算数值变量之间的相关系数"""
    if len(numeric_cols) < 2:
        return {"error": "数值列不足，无法计算相关性"}
    
    # 计算Pearson相关系数
    pearson_corr = df[numeric_cols].corr(method='pearson').round(3)
    
    # 计算Spearman相关系数
    spearman_corr = df[numeric_cols].corr(method='spearman').round(3)
    
    # 识别强相关变量对 (|r| > 0.7)
    strong_correlations = []
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            corr_value = pearson_corr.iloc[i, j]
            if abs(corr_value) > 0.7:
                strong_correlations.append({
                    "variable1": numeric_cols[i],
                    "variable2": numeric_cols[j],
                    "pearson_correlation": float(corr_value),
                    "correlation_type": "强正相关" if corr_value > 0 else "强负相关"
                })
    
    return {
        "pearson_correlation_matrix": pearson_corr.to_dict(),
        "spearman_correlation_matrix": spearman_corr.to_dict(),
        "strong_correlations": strong_correlations
    }

def analyze_categorical_vs_numeric(df: pd.DataFrame, cat_cols: List[str], num_cols: List[str]) -> Dict[str, Any]:
    """分析分类变量与数值变量之间的关系"""
    results = []
    
    for cat_col in cat_cols:
        if len(df[cat_col].unique()) > 10:  # 跳过唯一值过多的分类变量
            continue
            
        for num_col in num_cols:
            try:
                # 按分类变量分组
                groups = [df[df[cat_col] == val][num_col].dropna() for val in df[cat_col].unique()]
                
                # 只有当所有组都有足够的数据时才进行ANOVA分析
                if all(len(group) > 1 for group in groups) and len(groups) >= 2:
                    # 执行单因素方差分析(ANOVA)
                    f_stat, p_value = f_oneway(*groups)
                    
                    # 记录结果
                    result = {
                        "categorical_variable": cat_col,
                        "numeric_variable": num_col,
                        "f_statistic": float(f_stat),
                        "p_value": float(p_value),
                        "significant": p_value < 0.05
                    }
                    results.append(result)
            except Exception as e:
                print(f"分析 {cat_col} 与 {num_col} 时出错: {e}")
    
    return {"categorical_vs_numeric_analysis": results}

def main(file_path: str) -> Dict[str, Any]:
    """主函数，执行所有分析步骤"""
    # 加载数据
    df = load_data(file_path)
    
    # 获取数值列和分类列
    numeric_cols = get_numeric_columns(df)
    categorical_cols = get_categorical_columns(df)
    
    # 执行相关性分析
    correlation_results = calculate_correlations(df, numeric_cols)
    
    # 分析分类变量与数值变量之间的关系
    cat_num_results = analyze_categorical_vs_numeric(df, categorical_cols, numeric_cols)
    
    # 合并所有结果
    all_results = {
        "dataset_info": {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols
        },
        **correlation_results,
        **cat_num_results
    }
    
    return all_results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python script.py <数据文件路径>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    results = main(file_path)
    
    # 输出结果为JSON
    print(json.dumps(results, ensure_ascii=False, indent=2))