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
    """计算数值变量之间的相关性"""
    if len(numeric_cols) < 2:
        return {"error": "没有足够的数值列进行相关性分析"}
    
    # 计算Pearson相关系数
    pearson_corr = df[numeric_cols].corr(method='pearson').round(3)
    
    # 计算Spearman相关系数
    spearman_corr = df[numeric_cols].corr(method='spearman').round(3)
    
    # 识别强相关变量对 (|r| > 0.5)
    strong_correlations = []
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            col1, col2 = numeric_cols[i], numeric_cols[j]
            pearson_r = pearson_corr.loc[col1, col2]
            spearman_r = spearman_corr.loc[col1, col2]
            
            if abs(pearson_r) > 0.5:
                correlation_type = "正相关" if pearson_r > 0 else "负相关"
                strong_correlations.append({
                    "变量对": [col1, col2],
                    "Pearson相关系数": float(pearson_r),
                    "Spearman相关系数": float(spearman_r),
                    "相关类型": correlation_type,
                    "强度": "强" if abs(pearson_r) > 0.7 else "中等"
                })
    
    return {
        "pearson_correlation_matrix": pearson_corr.to_dict(),
        "spearman_correlation_matrix": spearman_corr.to_dict(),
        "strong_correlations": strong_correlations
    }

def analyze_categorical_vs_numeric(df: pd.DataFrame, cat_cols: List[str], 
                                  num_cols: List[str]) -> Dict[str, Any]:
    """分析分类变量与数值变量之间的关系"""
    results = {}
    
    for cat_col in cat_cols:
        cat_num_relations = {}
        for num_col in num_cols:
            # 执行单因素方差分析(ANOVA)
            try:
                groups = [df[df[cat_col] == category][num_col].values 
                         for category in df[cat_col].unique() if len(df[df[cat_col] == category]) > 0]
                
                if len(groups) > 1 and all(len(g) > 0 for g in groups):
                    f_stat, p_value = f_oneway(*groups)
                    
                    # 计算每个类别的均值
                    category_means = df.groupby(cat_col)[num_col].mean().to_dict()
                    
                    cat_num_relations[num_col] = {
                        "f_statistic": float(f_stat),
                        "p_value": float(p_value),
                        "significant": p_value < 0.05,
                        "category_means": category_means
                    }
            except Exception as e:
                cat_num_relations[num_col] = {"error": str(e)}
        
        results[cat_col] = cat_num_relations
    
    return results

def perform_correlation_analysis(file_path: str, output_path: str = 'correlation_analysis_results.json') -> None:
    """执行相关性分析并将结果保存为JSON"""
    # 加载数据
    df = load_data(file_path)
    
    # 获取数值列和分类列
    numeric_cols = get_numeric_columns(df)
    categorical_cols = get_categorical_columns(df)
    
    if len(numeric_cols) < 2:
        print("警告: 数据中没有足够的数值列进行相关性分析")
        results = {"error": "没有足够的数值列进行相关性分析"}
    else:
        # 执行相关性分析
        correlation_results = calculate_correlations(df, numeric_cols)
        
        # 分析分类变量与数值变量之间的关系
        cat_num_relations = analyze_categorical_vs_numeric(df, categorical_cols, numeric_cols)
        
        # 汇总结果
        results = {
            "numeric_correlations": correlation_results,
            "categorical_vs_numeric_relations": cat_num_relations,
            "analyzed_columns": {
                "numeric": numeric_cols,
                "categorical": categorical_cols
            },
            "data_summary": {
                "rows": len(df),
                "columns": len(df.columns)
            }
        }
    
    # 保存结果为JSON
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"相关性分析结果已保存到 {output_path}")
    except Exception as e:
        print(f"保存结果时出错: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("请输入CSV文件路径: ")
    
    perform_correlation_analysis(file_path)