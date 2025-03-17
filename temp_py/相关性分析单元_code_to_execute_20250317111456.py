import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime

# 创建保存图表的目录
if not os.path.exists('pngs'):
    os.makedirs('pngs')

# 读取CSV文件
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"成功读取数据，共 {df.shape[0]} 行，{df.shape[1]} 列")
        return df
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

# 分析数值列之间的相关性
def analyze_correlations(df):
    # 选择数值列
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    # 计算相关性矩阵
    corr_matrix = df[numeric_cols].corr()
    
    # 找出高相关性的列对
    high_corr_pairs = []
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            col1, col2 = numeric_cols[i], numeric_cols[j]
            corr = corr_matrix.loc[col1, col2]
            if abs(corr) > 0.7:  # 高相关性阈值
                high_corr_pairs.append((col1, col2, corr))
    
    # 按相关性绝对值排序
    high_corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    
    return corr_matrix, high_corr_pairs, numeric_cols

# 生成相关性热图
def plot_correlation_heatmap(corr_matrix, numeric_cols):
    plt.figure(figsize=(14, 12))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    sns.heatmap(corr_matrix, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
                square=True, linewidths=.5, annot=True, fmt=".2f", annot_kws={"size": 8})
    
    plt.title('Correlation Matrix of Network Performance Metrics', fontsize=16)
    plt.tight_layout()
    
    file_path = f"pngs/chart_corr_heatmap_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return file_path

# 生成散点图矩阵
def plot_scatter_matrix(df, high_corr_pairs):
    # 选择前5个高相关性的列对进行可视化
    top_pairs = high_corr_pairs[:min(5, len(high_corr_pairs))]
    scatter_plots = []
    
    for i, (col1, col2, corr) in enumerate(top_pairs):
        plt.figure(figsize=(10, 8))
        
        # 添加基站ID作为颜色区分
        sns.scatterplot(data=df, x=col1, y=col2, hue='base_station_id', alpha=0.6)
        
        plt.title(f'Correlation between {col1} and {col2} (r = {corr:.2f})', fontsize=14)
        plt.xlabel(col1.replace('_', ' ').title(), fontsize=12)
        plt.ylabel(col2.replace('_', ' ').title(), fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 添加回归线
        sns.regplot(data=df, x=col1, y=col2, scatter=False, line_kws={"color": "red"})
        
        plt.tight_layout()
        
        file_path = f"pngs/chart_corr_scatter_{i+1}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        scatter_plots.append({
            "file_path": file_path,
            "variables": [col1, col2],
            "correlation": corr
        })
    
    return scatter_plots

# 生成分组箱形图
def plot_boxplots(df):
    # 选择一些关键指标进行箱形图分析
    key_metrics = ['success_rate', 'signal_strength_dbm', 'latency_ms', 'packet_loss_percent']
    boxplot_files = []
    
    for metric in key_metrics:
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='base_station_id', y=metric, data=df)
        plt.title(f'{metric.replace("_", " ").title()} by Base Station', fontsize=14)
        plt.xlabel('Base Station ID', fontsize=12)
        plt.ylabel(metric.replace('_', ' ').title(), fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        file_path = f"pngs/chart_corr_boxplot_{metric}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        boxplot_files.append({
            "file_path": file_path,
            "metric": metric
        })
    
    return boxplot_files

# 将分析结果保存为JSON
def save_results_to_json(corr_matrix, high_corr_pairs, heatmap_path, scatter_plots, boxplot_files):
    results = {
        "analysis_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "correlation_summary": {
            "high_correlation_pairs": [
                {
                    "variable1": col1,
                    "variable2": col2,
                    "correlation": round(corr, 4)
                } for col1, col2, corr in high_corr_pairs
            ]
        },
        "visualizations": {
            "heatmap": heatmap_path,
            "scatter_plots": scatter_plots,
            "boxplots": boxplot_files
        },
        "findings": {
            "strongest_positive_correlation": max(high_corr_pairs, key=lambda x: x[2]) if high_corr_pairs else None,
            "strongest_negative_correlation": min(high_corr_pairs, key=lambda x: x[2]) if high_corr_pairs else None,
        }
    }
    
    output_file = f"correlation_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"分析结果已保存至 {output_file}")
    return output_file

# 主函数
def main():
    file_path = "temp_csv/excel_data_20250317111047.csv"
    
    # 读取数据
    df = load_data(file_path)
    if df is None:
        return
    
    # 分析相关性
    corr_matrix, high_corr_pairs, numeric_cols = analyze_correlations(df)
    
    # 生成热图
    heatmap_path = plot_correlation_heatmap(corr_matrix, numeric_cols)
    
    # 生成散点图
    scatter_plots = plot_scatter_matrix(df, high_corr_pairs)
    
    # 生成箱形图
    boxplot_files = plot_boxplots(df)
    
    # 保存结果
    json_file = save_results_to_json(corr_matrix, high_corr_pairs, heatmap_path, scatter_plots, boxplot_files)
    
    print(f"分析完成！热图已保存至 {heatmap_path}")
    print(f"发现了 {len(high_corr_pairs)} 对高相关性变量")

if __name__ == "__main__":
    main()