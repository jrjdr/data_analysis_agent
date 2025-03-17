import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

# 创建保存图表的目录
if not os.path.exists('pngs'):
    os.makedirs('pngs')

# 读取CSV文件
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return None

# 分析数据并生成图表
def analyze_data(df):
    if df is None or df.empty:
        return {"error": "数据为空或无法读取"}
    
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_summary": {
            "row_count": len(df),
            "column_count": len(df.columns)
        },
        "charts": []
    }
    
    # 图表1: 不同基站的平均信号强度和质量对比
    plt.figure(figsize=(12, 8))
    
    # 按基站分组计算平均信号强度和质量
    station_metrics = df.groupby('base_station_name')[['signal_strength_dbm', 'signal_quality_db']].mean().reset_index()
    
    x = np.arange(len(station_metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 8))
    rects1 = ax.bar(x - width/2, station_metrics['signal_strength_dbm'], width, label='Signal Strength (dBm)')
    rects2 = ax.bar(x + width/2, station_metrics['signal_quality_db'], width, label='Signal Quality (dB)')
    
    ax.set_title('Average Signal Strength and Quality by Base Station', fontsize=16)
    ax.set_xlabel('Base Station', fontsize=14)
    ax.set_ylabel('Value', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(station_metrics['base_station_name'], rotation=45, ha='right')
    ax.legend()
    
    # 添加数值标签
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    chart1_path = 'pngs/chart_bar_signal_by_station.png'
    plt.savefig(chart1_path)
    plt.close()
    
    # 保存图表1的结果
    results["charts"].append({
        "title": "Average Signal Strength and Quality by Base Station",
        "description": "Comparison of signal strength (dBm) and quality (dB) across different base stations",
        "file_path": chart1_path,
        "data": station_metrics.to_dict('records')
    })
    
    # 图表2: 不同信号类型的成功率和失败率对比
    signal_performance = df.groupby('signal_type')[['success_rate', 'failure_rate']].mean().reset_index()
    signal_performance = signal_performance.sort_values('success_rate', ascending=False)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    x = np.arange(len(signal_performance))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, signal_performance['success_rate'], width, label='Success Rate', color='green')
    rects2 = ax.bar(x + width/2, signal_performance['failure_rate'], width, label='Failure Rate', color='red')
    
    ax.set_title('Average Success and Failure Rates by Signal Type', fontsize=16)
    ax.set_xlabel('Signal Type', fontsize=14)
    ax.set_ylabel('Rate', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(signal_performance['signal_type'], rotation=45, ha='right')
    ax.legend()
    
    # 添加数值标签
    autolabel(rects1)
    autolabel(rects2)
    
    # 添加注释说明主要发现
    ax.text(0.5, -0.15, 
            "Key Finding: Signal types show significant variation in success rates, with some types consistently performing better.",
            horizontalalignment='center', fontsize=12, transform=ax.transAxes)
    
    plt.tight_layout()
    chart2_path = 'pngs/chart_bar_performance_by_signal_type.png'
    plt.savefig(chart2_path)
    plt.close()
    
    # 保存图表2的结果
    results["charts"].append({
        "title": "Average Success and Failure Rates by Signal Type",
        "description": "Comparison of success and failure rates across different signal types",
        "file_path": chart2_path,
        "data": signal_performance.to_dict('records')
    })
    
    return results

# 保存分析结果为JSON
def save_results(results, output_path="analysis_results.json"):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"分析结果已保存至 {output_path}")
    except Exception as e:
        print(f"保存结果时出错: {e}")

# 主函数
def main():
    file_path = "temp_csv/excel_data_20250317113651.csv"
    df = load_csv(file_path)
    if df is not None:
        results = analyze_data(df)
        save_results(results)
        print("分析完成，图表已保存在pngs目录下")

if __name__ == "__main__":
    main()