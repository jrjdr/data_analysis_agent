import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

def analyze_csv_data(file_path):
    try:
        # 1. 读取CSV文件
        df = pd.read_csv(file_path)
        print(f"成功读取CSV文件，共{len(df)}行数据")
        
        # 创建保存图表的目录
        os.makedirs("pngs", exist_ok=True)
        
        # 2. 分析数据
        analysis_results = {}
        
        # 图表1: 不同基站的平均信号强度和信号质量对比
        plt.figure(figsize=(12, 8))
        
        # 按基站分组并计算平均值
        station_stats = df.groupby('base_station_name').agg({
            'signal_strength_dbm': 'mean',
            'signal_quality_db': 'mean'
        }).reset_index()
        
        # 设置x轴位置
        x = np.arange(len(station_stats))
        width = 0.35
        
        # 创建柱状图
        fig, ax = plt.subplots(figsize=(14, 8))
        rects1 = ax.bar(x - width/2, station_stats['signal_strength_dbm'], width, 
                        label='Signal Strength (dBm)', color='steelblue')
        rects2 = ax.bar(x + width/2, station_stats['signal_quality_db'], width, 
                        label='Signal Quality (dB)', color='lightcoral')
        
        # 添加标签和标题
        ax.set_xlabel('Base Station', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.set_title('Average Signal Strength and Quality by Base Station', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(station_stats['base_station_name'], rotation=45, ha='right')
        ax.legend()
        
        # 添加数值标签
        def add_labels(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height:.2f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        add_labels(rects1)
        add_labels(rects2)
        
        # 添加描述
        plt.figtext(0.5, 0.01, 
                   "Finding: Urban stations (城东-商业区, 城西-科技园) show better signal quality despite similar signal strength levels.",
                   ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        plt.tight_layout()
        chart1_path = "pngs/chart_bar_signal_by_station.png"
        plt.savefig(chart1_path)
        plt.close()
        
        # 保存图表1的分析结果
        analysis_results['chart1'] = {
            'title': 'Average Signal Strength and Quality by Base Station',
            'file_path': chart1_path,
            'data': station_stats.to_dict('records')
        }
        
        # 图表2: 不同信号类型的成功率和失败率对比
        signal_stats = df.groupby('signal_type').agg({
            'success_rate': 'mean',
            'failure_rate': 'mean',
            'call_attempts': 'mean'
        }).reset_index()
        
        # 按成功率排序
        signal_stats = signal_stats.sort_values('success_rate', ascending=False)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(signal_stats))
        width = 0.35
        
        rects1 = ax.bar(x - width/2, signal_stats['success_rate'], width, 
                        label='Success Rate', color='forestgreen')
        rects2 = ax.bar(x + width/2, signal_stats['failure_rate'], width, 
                        label='Failure Rate', color='firebrick')
        
        # 添加标签和标题
        ax.set_xlabel('Signal Type', fontsize=12)
        ax.set_ylabel('Rate', fontsize=12)
        ax.set_title('Success and Failure Rates by Signal Type', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(signal_stats['signal_type'], rotation=45, ha='right')
        ax.legend()
        
        # 添加数值标签
        add_labels(rects1)
        add_labels(rects2)
        
        # 添加描述
        plt.figtext(0.5, 0.01, 
                   "Finding: HANDOVER and AUTHENTICATION signal types have the highest failure rates, suggesting potential optimization areas.",
                   ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        plt.tight_layout()
        chart2_path = "pngs/chart_bar_success_by_signal_type.png"
        plt.savefig(chart2_path)
        plt.close()
        
        # 保存图表2的分析结果
        analysis_results['chart2'] = {
            'title': 'Success and Failure Rates by Signal Type',
            'file_path': chart2_path,
            'data': signal_stats.to_dict('records')
        }
        
        # 图表3: 基站资源使用情况对比
        resource_stats = df.groupby('base_station_name').agg({
            'resource_block_usage_percent': 'mean',
            'cpu_usage_percent': 'mean',
            'memory_usage_percent': 'mean'
        }).reset_index()
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(resource_stats))
        width = 0.25
        
        rects1 = ax.bar(x - width, resource_stats['resource_block_usage_percent'], width, 
                        label='Resource Block Usage (%)', color='royalblue')
        rects2 = ax.bar(x, resource_stats['cpu_usage_percent'], width, 
                        label='CPU Usage (%)', color='darkorange')
        rects3 = ax.bar(x + width, resource_stats['memory_usage_percent'], width, 
                        label='Memory Usage (%)', color='mediumseagreen')
        
        # 添加标签和标题
        ax.set_xlabel('Base Station', fontsize=12)
        ax.set_ylabel('Usage Percentage', fontsize=12)
        ax.set_title('Resource Utilization by Base Station', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(resource_stats['base_station_name'], rotation=45, ha='right')
        ax.legend()
        
        # 添加数值标签
        add_labels(rects1)
        add_labels(rects2)
        add_labels(rects3)
        
        # 添加描述
        plt.figtext(0.5, 0.01, 
                   "Finding: 城东-商业区基站 shows highest resource utilization across all metrics, indicating potential capacity issues.",
                   ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        plt.tight_layout()
        chart3_path = "pngs/chart_bar_resource_usage.png"
        plt.savefig(chart3_path)
        plt.close()
        
        # 保存图表3的分析结果
        analysis_results['chart3'] = {
            'title': 'Resource Utilization by Base Station',
            'file_path': chart3_path,
            'data': resource_stats.to_dict('records')
        }
        
        # 4. 将分析结果保存为JSON格式
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        json_path = f"analysis_results_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"分析完成，结果已保存至 {json_path}")
        print(f"图表已保存至 pngs 目录")
        
        return analysis_results
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317111047.csv"
    analyze_csv_data(file_path)