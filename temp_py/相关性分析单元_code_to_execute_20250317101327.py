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
                    f_stat, p_value = f_oneway(*groups)
                    
                    results.append({
                        "categorical_variable": cat_col,
                        "numeric_variable": num_col,
                        "f_statistic": float(f_stat),
                        "p_value": float(p_value),
                        "significant_relationship": p_value < 0.05
                    })
            except Exception as e:
                print(f"分析 {cat_col} 和 {num_col} 时出错: {e}")
    
    return {"categorical_vs_numeric_analysis": results}

def calculate_partial_correlations(df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
    """计算部分相关系数，控制其他变量的影响"""
    if len(numeric_cols) < 3:  # 需要至少3个变量才能计算部分相关系数
        return {"partial_correlations": "变量不足，无法计算部分相关系数"}
    
    partial_corrs = []
    
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            var1 = numeric_cols[i]
            var2 = numeric_cols[j]
            control_vars = [col for col in numeric_cols if col != var1 and col != var2]
            
            # 选择最多5个控制变量，避免计算过于复杂
            if len(control_vars) > 5:
                control_vars = control_vars[:5]
            
            try:
                # 计算部分相关系数
                x = df[var1].values
                y = df[var2].values
                z = df[control_vars].values
                
                # 使用偏相关系数公式计算
                r_xy = np.corrcoef(x, y)[0, 1]
                r_xz = np.corrcoef(x, z.T)[0, 1:]
                r_yz = np.corrcoef(y, z.T)[0, 1:]
                
                # 避免除以零
                if np.all(np.abs(r_xz) < 1) and np.all(np.abs(r_yz) < 1):
                    numerator = r_xy - np.sum(r_xz * r_yz)
                    denominator = np.sqrt((1 - np.sum(r_xz**2)) * (1 - np.sum(r_yz**2)))
                    
                    if denominator != 0:
                        partial_corr = numerator / denominator
                        
                        if abs(partial_corr) > 0.5:  # 只保存较强的部分相关
                            partial_corrs.append({
                                "variable1": var1,
                                "variable2": var2,
                                "control_variables": control_vars,
                                "partial_correlation": float(partial_corr)
                            })
            except Exception as e:
                continue
    
    return {"partial_correlations": partial_corrs}

def main():
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    # 加载数据
    df = load_data(file_path)
    
    # 获取数值列和分类列
    numeric_cols = get_numeric_columns(df)
    categorical_cols = get_categorical_columns(df)
    
    if len(numeric_cols) < 2:
        print("数据中没有足够的数值列进行相关性分析")
        sys.exit(1)
    
    # 执行相关性分析
    results = {}
    
    # 1. 数值变量之间的相关性
    correlation_results = calculate_correlations(df, numeric_cols)
    results.update(correlation_results)
    
    # 2. 分类变量与数值变量之间的关系
    if categorical_cols:
        cat_num_results = analyze_categorical_vs_numeric(df, categorical_cols, numeric_cols)
        results.update(cat_num_results)
    
    # 3. 部分相关性分析
    partial_corr_results = calculate_partial_correlations(df, numeric_cols)
    results.update(partial_corr_results)
    
    # 4. 添加基本统计信息
    results["analysis_metadata"] = {
        "file_analyzed": file_path,
        "total_rows": len(df),
        "numeric_variables_analyzed": numeric_cols,
        "categorical_variables_analyzed": categorical_cols,
        "analysis_timestamp": pd.Timestamp.now().isoformat()
    }
    
    # 保存结果到JSON文件
    output_file = 'correlation_analysis_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"相关性分析完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    main()