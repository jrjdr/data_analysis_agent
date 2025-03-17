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
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共{df.shape[0]}行，{df.shape[1]}列")
        return df
    except Exception as e:
        print(f"加载数据失败: {e}")
        sys.exit(1)

def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """获取数据框中的数值型列"""
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    print(f"找到{len(numeric_cols)}个数值型列")
    return numeric_cols

def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """获取数据框中的分类型列"""
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    print(f"找到{len(cat_cols)}个分类型列")
    return cat_cols

def calculate_correlation_matrix(df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
    """计算数值列之间的相关性矩阵"""
    # 计算Pearson相关系数
    pearson_corr = df[numeric_cols].corr(method='pearson').round(3)
    # 计算Spearman相关系数
    spearman_corr = df[numeric_cols].corr(method='spearman').round(3)
    
    # 提取强相关变量对（相关系数绝对值大于0.7）
    strong_correlations = []
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            var1, var2 = numeric_cols[i], numeric_cols[j]
            pearson_value = pearson_corr.loc[var1, var2]
            spearman_value = spearman_corr.loc[var1, var2]
            
            if abs(pearson_value) > 0.7 or abs(spearman_value) > 0.7:
                strong_correlations.append({
                    'variable1': var1,
                    'variable2': var2,
                    'pearson_correlation': float(pearson_value),
                    'spearman_correlation': float(spearman_value),
                    'correlation_strength': 'Strong Positive' if pearson_value > 0.7 else 'Strong Negative'
                })
    
    return {
        'pearson_correlation_matrix': pearson_corr.to_dict(),
        'spearman_correlation_matrix': spearman_corr.to_dict(),
        'strong_correlations': strong_correlations
    }

def analyze_categorical_numeric_relationships(df: pd.DataFrame, cat_cols: List[str], 
                                             numeric_cols: List[str]) -> List[Dict[str, Any]]:
    """分析分类变量与数值变量之间的关系"""
    relationships = []
    
    for cat_col in cat_cols:
        if len(df[cat_col].unique()) > 30:  # 如果分类变量取值太多，跳过
            continue
            
        for num_col in numeric_cols:
            # 对每个分类变量的每个取值，提取对应的数值变量值
            groups = []
            group_names = []
            
            for category in df[cat_col].unique():
                group_data = df[df[cat_col] == category][num_col].dropna()
                if len(group_data) > 5:  # 确保每组有足够的数据
                    groups.append(group_data)
                    group_names.append(category)
            
            if len(groups) >= 2:  # 至少需要两组才能进行ANOVA
                try:
                    # 执行单因素方差分析
                    f_stat, p_value = f_oneway(*groups)
                    
                    # 计算每个组的统计数据
                    group_stats = {}
                    for i, category in enumerate(group_names):
                        group_stats[str(category)] = {
                            'mean': float(groups[i].mean()),
                            'std': float(groups[i].std()),
                            'count': int(len(groups[i]))
                        }
                    
                    relationships.append({
                        'categorical_variable': cat_col,
                        'numeric_variable': num_col,
                        'f_statistic': float(f_stat),
                        'p_value': float(p_value),
                        'significant': bool(p_value < 0.05),  # 显式转换为Python的bool类型
                        'group_statistics': group_stats
                    })
                except Exception as e:
                    print(f"ANOVA分析失败 {cat_col} vs {num_col}: {e}")
    
    return relationships

class NumpyEncoder(json.JSONEncoder):
    """处理NumPy数据类型的JSON编码器"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif pd.isna(obj):
            return None
        return super(NumpyEncoder, self).default(obj)

def main():
    if len(sys.argv) != 2:
        print("用法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        sys.exit(1)
    
    # 加载数据
    df = load_data(file_path)
    
    # 获取数值列和分类列
    numeric_cols = get_numeric_columns(df)
    categorical_cols = get_categorical_columns(df)
    
    if len(numeric_cols) < 2:
        print("错误: 数据中没有足够的数值列进行相关性分析")
        sys.exit(1)
    
    # 执行相关性分析
    results = {}
    
    # 1. 数值变量之间的相关性
    print("计算数值变量之间的相关性...")
    results['numeric_correlations'] = calculate_correlation_matrix(df, numeric_cols)
    
    # 2. 分类变量与数值变量之间的关系
    print("分析分类变量与数值变量之间的关系...")
    results['categorical_numeric_relationships'] = analyze_categorical_numeric_relationships(
        df, categorical_cols, numeric_cols)
    
    # 3. 添加元数据
    results['metadata'] = {
        'file_analyzed': file_path,
        'total_rows': int(df.shape[0]),
        'total_columns': int(df.shape[1]),
        'numeric_columns': numeric_cols,
        'categorical_columns': categorical_cols,
        'analysis_timestamp': pd.Timestamp.now().isoformat()
    }
    
    # 保存结果到JSON文件
    output_file = 'correlation_analysis_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
    
    print(f"分析完成，结果已保存到 {output_file}")

if __name__ == "__main__":
    main()