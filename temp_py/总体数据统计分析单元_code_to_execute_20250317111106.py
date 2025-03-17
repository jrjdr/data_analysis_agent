import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime

# 读取CSV文件
def read_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

# 基本描述性统计分析
def basic_stats(df):
    return df.describe().to_dict()

# 分析数值列和分类列的分布
def analyze_distributions(df):
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    numeric_dist = {col: df[col].value_counts().to_dict() for col in numeric_cols}
    categorical_dist = {col: df[col].value_counts().to_dict() for col in categorical_cols}
    
    return {"numeric": numeric_dist, "categorical": categorical_dist}

# 生成图表
def generate_charts(df):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='base_station_name', y='success_rate', data=df)
    plt.title('Success Rate by Base Station')
    plt.xlabel('Base Station')
    plt.ylabel('Success Rate')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('pngs/chart_stats_success_rate.png')
    plt.close()

    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='active_users', y='downlink_throughput_mbps', hue='signal_type', data=df)
    plt.title('Downlink Throughput vs Active Users by Signal Type')
    plt.xlabel('Active Users')
    plt.ylabel('Downlink Throughput (Mbps)')
    plt.legend(title='Signal Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('pngs/chart_stats_throughput_users.png')
    plt.close()

# 保存分析结果为JSON
def save_results(stats, distributions, chart_paths):
    results = {
        "basic_stats": stats,
        "distributions": distributions,
        "charts": chart_paths
    }
    with open('analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)

# 主函数
def main():
    file_path = "temp_csv/excel_data_20250317111047.csv"
    df = read_csv(file_path)
    
    if df is None:
        return
    
    stats = basic_stats(df)
    distributions = analyze_distributions(df)
    
    if not os.path.exists('pngs'):
        os.makedirs('pngs')
    
    generate_charts(df)
    
    chart_paths = [
        "pngs/chart_stats_success_rate.png",
        "pngs/chart_stats_throughput_users.png"
    ]
    
    save_results(stats, distributions, chart_paths)
    
    print("Analysis completed. Results saved in analysis_results.json and charts in pngs folder.")

if __name__ == "__main__":
    main()