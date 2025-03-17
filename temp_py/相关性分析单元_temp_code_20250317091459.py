import pandas as pd
import numpy as np
import scipy.stats as stats
import json
import sys
import os
from sklearn.feature_selection import f_classif
from scipy.stats import chi2_contingency

def load_data(file_path):
    """加载CSV数据文件"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共{df.shape[0]}行，{df.shape[1]}列")
        return df
    except Exception as e:
        print(f"加载数据失败: {e}")
        sys.exit(1)

def analyze_correlations(df):
    """分析数据中的相关性"""
    results = {}
    
    # 1. 提取数值列和分类列
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if len(numeric_cols) < 2:
        print("警告: 数据中数值列少于2个，无法进行完整的相关性分析")
        results["warning"] = "数据中数值列少于2个，相关性分析有限"
    
    # 2. 数值变量之间的相关性分析
    if len(numeric_cols) >= 2:
        # Pearson相关系数（线性关系）
        pearson_corr = df[numeric_cols].corr(method='pearson').round(3)
        # Spearman相关系数（单调关系，对异常值不敏感）
        spearman_corr = df[numeric_cols].corr(method='spearman').round(3)
        
        # 提取强相关变量对（绝对值大于0.5）
        strong_pearson_pairs = []
        strong_spearman_pairs = []
        
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                col1, col2 = numeric_cols[i], numeric_cols[j]
                p_corr = pearson_corr.loc[col1, col2]
                s_corr = spearman_corr.loc[col1, col2]
                
                if abs(p_corr) > 0.5:
                    strong_pearson_pairs.append({
                        "variable1": col1,
                        "variable2": col2,
                        "correlation": float(p_corr),
                        "strength": "强" if abs(p_corr) > 0.7 else "中等",
                        "direction": "正相关" if p_corr > 0 else "负相关"
                    })
                
                if abs(s_corr) > 0.5:
                    strong_spearman_pairs.append({
                        "variable1": col1,
                        "variable2": col2,
                        "correlation": float(s_corr),
                        "strength": "强" if abs(s_corr) > 0.7 else "中等",
                        "direction": "正相关" if s_corr > 0 else "负相关"
                    })
        
        results["numeric_correlations"] = {
            "pearson": pearson_corr.to_dict(),
            "spearman": spearman_corr.to_dict(),
            "strong_pearson_pairs": strong_pearson_pairs,
            "strong_spearman_pairs": strong_spearman_pairs
        }
    
    # 3. 分类变量与数值变量之间的关系分析
    cat_num_relations = []
    
    for cat_col in categorical_cols:
        for num_col in numeric_cols:
            try:
                # 使用ANOVA分析分类变量与数值变量的关系
                categories = df[cat_col].unique()
                if len(categories) <= 10:  # 限制类别数量，避免过多类别
                    f_stat, p_value = f_classif(
                        df[[num_col]], 
                        df[cat_col]
                    )
                    
                    if p_value[0] < 0.05:
                        cat_num_relations.append({
                            "categorical_var": cat_col,
                            "numeric_var": num_col,
                            "f_statistic": float(f_stat[0]),
                            "p_value": float(p_value[0]),
                            "significant": True
                        })
                    else:
                        cat_num_relations.append({
                            "categorical_var": cat_col,
                            "numeric_var": num_col,
                            "f_statistic": float(f_stat[0]),
                            "p_value": float(p_value[0]),
                            "significant": False
                        })
            except Exception as e:
                print(f"分析 {cat_col} 和 {num_col} 关系时出错: {e}")
    
    results["categorical_numeric_relations"] = cat_num_relations
    
    # 4. 分类变量之间的关系分析（卡方检验）
    if len(categorical_cols) >= 2:
        cat_cat_relations = []
        
        for i in range(len(categorical_cols)):
            for j in range(i+1, len(categorical_cols)):
                cat1, cat2 = categorical_cols[i], categorical_cols[j]
                try:
                    # 创建列联表
                    contingency_table = pd.crosstab(df[cat1], df[cat2])
                    
                    # 执行卡方检验
                    chi2, p, dof, expected = chi2_contingency(contingency_table)
                    
                    cat_cat_relations.append({
                        "variable1": cat1,
                        "variable2": cat2,
                        "chi2": float(chi2),
                        "p_value": float(p),
                        "significant": p < 0.05
                    })
                except Exception as e:
                    print(f"分析 {cat1} 和 {cat2} 关系时出错: {e}")
        
        results["categorical_relations"] = cat_cat_relations
    
    return results

def save_results(results, output_file='correlation_analysis_results.json'):
    """将结果保存为JSON文件"""
    try:
        # 将NumPy类型转换为Python原生类型
        def convert_to_native(obj):
            if isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(i) for i in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return convert_to_native(obj.tolist())
            else:
                return obj
        
        results = convert_to_native(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到 {output_file}")
    except Exception as e:
        print(f"保存结果失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        sys.exit(1)
    
    # 加载数据
    df = load_data(file_path)
    
    # 分析相关性
    results = analyze_correlations(df)
    
    # 保存结果
    save_results(results)

if __name__ == "__main__":
    main()